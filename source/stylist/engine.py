#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Core of the Fortran style checking tool.
'''
import logging
from typing import List

import stylist.issue
import stylist.source
import stylist.style


class CheckEngine(object):
    # pylint: disable=too-few-public-methods
    '''
    Manages the checking of Fortran source files against style lists.
    '''

    def __init__(self, styles: List[stylist.style.Style]):
        '''
        Constructs a CheckEngine object from list of style lists.

        styles (list) Style object for each style list to use in checks.
        '''
        self._styles = styles

    def check(self, source_filename: str) -> List[stylist.issue.Issue]:
        '''
        Passes the eyes of all registered style lists over the source file.

        source_filename (string or file-like) Fortran source file to check.
        '''
        issues = []
        with open(source_filename, 'rt') as source_file:
            logging.getLogger(__name__).info('Examining: ' + source_filename)
            source = stylist.source.SourceFactory.read_file(source_file)
            for astyle in self._styles:
                for new_issue in astyle.check(source):
                    new_issue.set_filename(source_filename)
                    issues.append(new_issue)
        return issues
