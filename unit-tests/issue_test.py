#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the Issue object functions as expected.
"""

import stylist.issue


def test_constructor() -> None:
    """
    Checks the constructor works.
    """
    unit_under_test = stylist.issue.Issue('Teapot cheese')
    assert str(unit_under_test) == 'Teapot cheese'
