#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
None language specific rules.
"""
from abc import ABCMeta, abstractmethod
import logging
import re
from typing import List

from stylist.issue import Issue
from stylist.source import SourceText


class Rule(object, metaclass=ABCMeta):
    """
    Abstract parent of all rules.
    """
    @abstractmethod
    def examine(self, subject) -> List[Issue]:
        """
        Examines the provided source code object for an issue.
        """
        message = 'Rule: {name}'.format(name=str(self.__class__.__name__))
        logging.getLogger(__name__).info(message)
        return []


class TrailingWhitespace(Rule):
    """
    Scans the source for tailing whitespace.
    """
    _TRAILING_SPACE_PATTERN = re.compile(r'\s+$')

    def examine(self, subject: SourceText) -> List[Issue]:
        """
        Examines the text for white space at the end of lines.
        This includes lines which consist entirely of white space.
        """
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
