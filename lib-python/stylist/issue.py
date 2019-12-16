#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Issues found in the source.
'''
from __future__ import absolute_import, division, print_function


class Issue(object):
    # pylint: disable=too-few-public-methods
    '''
    Holds details pertaining to an issue with the source.
    '''
    def __init__(self, description, line=None, filename=None):
        self._filename = filename
        self._line = line
        self._description = description

    def __str__(self):
        string = ''
        if self._filename:
            string += '{filename}: '
        if self._line:
            string += '{line}: '
        string += '{description}'
        return string.format(filename=self._filename,
                             line=self._line,
                             description=self._description)

    def set_filename(self, filename):
        '''
        Attaches a filename to this issue.
        '''
        self._filename = filename
