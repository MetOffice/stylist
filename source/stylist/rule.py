#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
A collection of style rules.
'''

from abc import ABCMeta, abstractmethod
import logging
import re

from stylist.issue import Issue
from stylist.source import FortranSource


class Rule(object, metaclass=ABCMeta):
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


class TrailingWhitespace(Rule):
    '''
    Scans the source for tailing whitespace.
    '''
    _TRAILING_SPACE_PATTERN = re.compile(r'\s+$')

    def examine(self, subject):
        '''
        Examines the text for white space at the end of lines.

        This includes empty lines.
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


class FortranRule(Rule, metaclass=ABCMeta):
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
