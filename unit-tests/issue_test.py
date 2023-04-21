#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the Issue object functions as expected.
"""
from pathlib import Path

from stylist.issue import Issue


def test_constructor() -> None:
    """
    Checks the constructor works.
    """
    unit_under_test = Issue('Teapot cheese')
    assert str(unit_under_test) == 'Teapot cheese'


def test_sortability() -> None:
    """
    Checks a list of Item can be sorted.
    """
    test_list = [Issue("With line number and file", 12, Path('cheese.txt')),
                 Issue("Without line number or file"),
                 Issue("With line number but not file", 27),
                 Issue("Without line number but with file",
                       filename=Path('beef.txt')),
                 Issue("With everything again", 39, Path('cheese.txt'))]
    test_list.sort()
    assert [str(issue) for issue in test_list] \
           == ['Without line number or file',
               '27: With line number but not file',
               'beef.txt: Without line number but with file',
               'cheese.txt: 12: With line number and file',
               'cheese.txt: 39: With everything again']
