##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
None language specific rules.
"""
from abc import ABC, abstractmethod
import re
from typing import List

from stylist.issue import Issue
from stylist.source import SourceText


class Rule(ABC):
    """
    Abstract parent of all rules.
    """
    @abstractmethod
    def examine(self, subject) -> List[Issue]:
        """
        Examines the provided source code object for issues.

        :param subject: The source file to be examined.
        :return: All issues found with the source.
        """
        raise NotImplementedError()


class TrailingWhitespace(Rule):
    """
    Examines the text for white space at the end of lines.
    This includes lines which consist entirely of white space.
    """
    _TRAILING_SPACE_PATTERN = re.compile(r'\s+$')

    def examine(self, subject: SourceText) -> List[Issue]:
        issues = []
        text = subject.get_text()
        line_tally = 0
        for line in text.splitlines():
            line_tally += 1
            match = self._TRAILING_SPACE_PATTERN.search(line)
            if match:
                description = 'Found trailing white space'
                issues.append(Issue(description, line=line_tally))

        return issues
