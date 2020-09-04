#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Core of the style checking tool.
"""
import logging
from typing import Sequence

from stylist.issue import Issue
from stylist.source import SourceFactory
from stylist.style import Style


class CheckEngine(object):
    """
    Manages the checking of source files against style lists.
    """
    def __init__(self, styles: Sequence[Style]) -> None:
        """
        Constructs a CheckEngine object from list of style lists.
        """
        self._styles = styles

    def check(self, source_filename: str) -> Sequence[Issue]:
        """
        Passes the eyes of all registered style lists over the source file.
        """
        issues = []
        with open(source_filename, 'rt') as source_file:
            logging.getLogger(__name__).info('Examining: ' + source_filename)
            source = SourceFactory.read_file(source_file)
            for astyle in self._styles:
                for new_issue in astyle.check(source):
                    new_issue.set_filename(source_filename)
                    issues.append(new_issue)
        issues.sort(key=lambda x: (x.filename, x.line, x.description))
        return issues
