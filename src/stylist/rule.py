#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
A collection of style rules.
'''
from __future__ import absolute_import, division, print_function

from abc import ABCMeta, abstractmethod
import logging
import re
from six import add_metaclass

import fparser.two.Fortran2003
import fparser.common.readfortran
from stylist.issue import Issue
from stylist.source import FortranSource


@add_metaclass(ABCMeta)
class Rule(object):
    # pylint: disable=too-few-public-methods
    '''
    Abstract parent of all rules.
    '''
    @abstractmethod
    def examine(self, subject):
        '''
        Examines the provided source code object for an issue.

        Returns a list of stylist.issue.Issue. Naturally this may be an
        empty list if all was well.
        '''
        message = 'Rule: {name}'.format(name=str(self.__class__.__name__))
        logging.getLogger(__name__).info(message)
        return []


class FortranCharacterset(Rule):
    # pylint: disable=too-few-public-methods
    '''
    Scans the source for characters which are not supported by Fortran.
    '''
    _FORTRAN_LETTER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    _FORTRAN_DIGIT = '0123456789'
    _FORTRAN_ALPHANUMERIC = _FORTRAN_LETTER + _FORTRAN_DIGIT + '_'
    _FORTRAN_SPECIALS = ' =+-*/\\()[]{},.:;!"%&~<>?\'`^|$#@'
    _FORTRAN_CHARACTERSET = _FORTRAN_ALPHANUMERIC + _FORTRAN_SPECIALS

    _APOSTROPHY = "'"
    _EXCLAMATION = '!'
    _NEWLINE = '\n'
    _QUOTE = '"'

    def examine(self, subject):
        # pylint: disable=too-many-branches
        '''
        Examines the source code for none Fortran characters.

        This is complicated by the fact that the source must consist of only
        certain characters except comments and strings. These may contain
        anything.
        '''
        issues = super(FortranCharacterset, self).examine(subject)

        text = subject.get_text()
        index = 0
        line = 1
        state = 'code'
        while index < len(text):
            character = text[index]
            if state == 'code':
                if character == self._NEWLINE:
                    line += 1
                elif character == self._EXCLAMATION:
                    state = 'comment'
                elif character == self._APOSTROPHY:
                    state = 'apostraphystring'
                elif character == self._QUOTE:
                    state = 'quotestring'
                elif character in self._FORTRAN_CHARACTERSET:
                    pass
                else:
                    description = "Found character {char} " \
                                  + "not in Fortran character set"
                    description = description.format(char=repr(character))
                    issues.append(Issue(description, line=line))
            elif state == 'comment':
                if character == self._NEWLINE:
                    line += 1
                    state = 'code'
            elif state == 'apostraphystring':
                if character == self._APOSTROPHY:
                    state = 'code'
            elif state == 'quotestring':
                if character == self._QUOTE:
                    state = 'code'
            else:
                raise Exception('Parser in unknown state: ' + state)
            index += 1

        return issues


class TrailingWhitespace(Rule):
    '''
    Scans the source for tailing whitespace.
    '''
    _TRAILING_SPACE_PATTERN = re.compile(r'\s+$')

    def examine(self, subject):
        '''
        Examines the text for white space at the end of lines. This includes empty lines.
        :param subject: File contents as Source object.
        :return: List of issues or empty list.
        '''
        issues = super(TrailingWhitespace, self).examine(subject)

        text = subject.get_text()
        line_tally = 0
        for line in text.splitlines():
            line_tally += 1
            match = self._TRAILING_SPACE_PATTERN.search(line)
            if match:
                description = 'Found trailing white space'
                issues.append(Issue(description, line=line_tally))

        return issues


@add_metaclass(ABCMeta)
class FortranRule(Rule):
    '''
    Parent for style rules pertaining to Fortran source.
    '''
    # pylint: disable=too-few-public-methods, abstract-method
    def examine(self, subject):
        issues = super(FortranRule, self).examine(subject)

        if not isinstance(subject, FortranSource):
            description = '"{0}" passed to a Fortran rule'
            raise Exception(description.format(subject.get_language()))

        if not subject.get_tree():
            description = 'Unable to perform {} as source didn\'t parse: {}'
            issues.append(Issue(description.format(self.__class__.__name__,
                                                   subject.get_tree_error())))
            return issues

        issues.extend(self.examine_fortran(subject))
        return issues

    @abstractmethod
    def examine_fortran(self, subject):
        '''
        Examines the provided Fortran source code object for an issue.

        Returns a list of stylist.issue.Issue objects.
        '''
        raise NotImplementedError()


class MissingImplicit(FortranRule):
    # pylint: disable=too-few-public-methods
    '''
    Catches cases where code blocks which could have an "implicit" statement
    don't.
    '''
    def __init__(self, default):
        '''
        Constructor taking a default implication.

        Todo: This rule was designed to check merely for the presence of an
        "implicit" statement but to leave the choice of implication to the
        user. It might also be desirable to allow this rule to enforce a
        specific implication. In which case the "default" argument may need a
        different name. A switch would be necessary to flip between "any" and
        "specific" modes.

        Todo: At the moment the default is not used. In the future we may want
        to allow rules to enforce style rather than simply reporting it. In
        this case the default would be used where none is present.
        '''
        assert default.lower() in ('none', 'private', 'public')
        self._default = default.lower()

    _NATURE_MAP = {fparser.two.Fortran2003.Program_Stmt: 'Program',
                   fparser.two.Fortran2003.Module_Stmt: 'Module',
                   fparser.two.Fortran2003.Subroutine_Stmt: 'Subroutine',
                   fparser.two.Fortran2003.Function_Stmt: 'Function'}

    def examine_fortran(self, subject):
        issues = []

        scope_units = subject.path('Program_Unit')
        scope_units.extend(subject.path(['Main_Program',
                                         'Internal_Subprogram_Part',
                                         'Internal_Subprogram']))
        scope_units.extend(subject.path(['Module',
                                         'Module_Subprogram_Part',
                                         'Module_Subprogram']))
        for scope in scope_units:
            scope_statement = subject.get_first_statement(root=scope)

            implication = subject.path(['Specification_Part',
                                        'Implicit_Part',
                                        'Implicit_Stmt'],
                                       root=scope.content[1:])
            if not implication:
                nature = MissingImplicit._NATURE_MAP[scope_statement.__class__]
                name = scope_statement.items[1]
                description = "{thing} '{name}' is missing " \
                              + "an implicit statement"
                description = description.format(thing=nature, name=name)
                issues.append(Issue(description))
        return issues


class MissingOnly(FortranRule):
    '''
    Catches cases where a "use" statement is present but has no "only" claus.
    '''
    def __init__(self, ignore=[]):
        '''
        Constructs a "MissingOnly" rule object taking a list of exception
        modules which are not required to have an "only" clause.
        '''
        assert isinstance(ignore, list)
        self._ignore = ignore

    def examine_fortran(self, subject):
        issues = []

        for statement in subject.find_all(fparser.two.Fortran2003.Use_Stmt):
            module = statement.items[2]
            onlies = statement.items[4]
            if str(module).lower() not in self._ignore:
                if onlies is None:
                    description = 'Usage of "{module}" without "only" clause.'
                    issues.append(Issue(description.format(module=module)))

        return issues
