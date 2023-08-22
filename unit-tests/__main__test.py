#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright 2023 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests the reporting of error conditions.
"""
from pathlib import Path

from pytest import raises

from stylist import StylistException
from stylist.__main__ import perform
from stylist.configuration import Configuration
from stylist.style import Style


def test_no_style(tmp_path: Path):
    """
    Checks that an appropriate error is generated if no style is defined.
    """
    (tmp_path / 'foo.f90').write_text("foo")
    configuration = Configuration()  # There is no style here
    with raises(StylistException) as ex:
        _ = perform(configuration, [tmp_path], [], [], verbose=False)
    assert ex.value.message == "No styles are defined by the configuration."


def test_missing_style(tmp_path: Path):
    """
    Checks that A useful error is generated if a non-existent style is
    requested.
    """
    (tmp_path / 'bar.f90').write_text("bar")
    configuration = Configuration()
    configuration.add_style('existent', Style())
    with raises(StylistException) as ex:
        _ = perform(configuration, [tmp_path], ['missing'], [], verbose=False)
    assert ex.value.message \
           == 'Style "missing" is not defined by the configuration.'
