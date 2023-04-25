#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Extensible code style checker currently supporting Fortran, PSyclone DSL, etc
"""

__version__ = '0.4.0'


class StylistException(Exception):
    """
    Allows exceptions from stylist to be distinguished from other exceptions.
    """
    pass
