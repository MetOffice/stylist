#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Rules relating to Fortran source.
'''

from typing import List

import fparser  # type: ignore

from stylist.issue import Issue
from stylist.rule import Rule, FortranRule
from stylist.source import FortranSource


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

    def examine(self, subject: FortranSource) -> List[Issue]:
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


class MissingImplicit(FortranRule):
    # pylint: disable=too-few-public-methods
    '''
    Catches cases where code blocks which could have an "implicit" statement
    don't.
    '''
    def __init__(self, default: str):
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

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
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
    def __init__(self, ignore: List[str] = []):
        '''
        Constructs a "MissingOnly" rule object taking a list of exception
        modules which are not required to have an "only" clause.
        '''
        assert isinstance(ignore, list)
        self._ignore = ignore

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues = []

        for statement in subject.find_all(fparser.two.Fortran2003.Use_Stmt):
            module = statement.items[2]
            onlies = statement.items[4]
            if str(module).lower() not in self._ignore:
                if onlies is None:
                    description = 'Usage of "{module}" without "only" clause.'
                    issues.append(Issue(description.format(module=module)))

        return issues
