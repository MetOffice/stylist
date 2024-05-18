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
from pytest import raises, fixture

from stylist import StylistException
from stylist.__main__ import perform, __configure
import stylist.__main__ as maintest
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


@fixture(scope="session")
def site_config(tmp_path_factory):
    site = tmp_path_factory.mktemp("data") / "site.py"
    site.write_text("\n".join([
        "from stylist.source import FilePipe, PlainText",
        "from stylist.rule import LimitLineLength",
        "from stylist.style import Style",
        "txt = FilePipe(PlainText)",
        "foo = Style(LimitLineLength(80))",
    ]))

    return site


@fixture(scope="session")
def user_config(tmp_path_factory):
    user = tmp_path_factory.mktemp("data") / "user.py"
    user.write_text("\n".join([
        "from stylist.source import FilePipe, PlainText",
        "from stylist.rule import TrailingWhitespace",
        "from stylist.style import Style",
        "txt = FilePipe(PlainText)",
        "bar = Style(TrailingWhitespace())",
    ]))

    return user


@fixture(scope="session")
def project_config(tmp_path_factory):
    project = tmp_path_factory.mktemp("data") / "project.py"
    project.write_text("\n".join([
        "from stylist.source import FilePipe, PlainText",
        "from stylist.rule import LimitLineLength, TrailingWhitespace",
        "from stylist.style import Style",
        "txt = FilePipe(PlainText)",
        "foo = Style(LimitLineLength(80), TrailingWhitespace)",
    ]))

    return project


def test_no_configurations(tmp_path):

    maintest.site_file = None
    maintest.user_file = None

    configuration = __configure(None)
    assert configuration is None


def test_site_only_configuration(site_config):

    maintest.site_file = site_config
    maintest.user_file = None

    configuration = __configure(None)
    assert configuration is not None
    assert list(configuration.styles) == ["foo"]
    assert len(configuration.styles["foo"].list_rules()) == 1


def test_user_only_configuration(user_config):

    maintest.site_file = None
    maintest.user_file = user_config

    configuration = __configure(None)
    assert configuration is not None
    assert list(configuration.styles) == ["bar"]
    assert len(configuration.styles["bar"].list_rules()) == 1


def test_user_and_site_configurations(site_config, user_config):

    maintest.site_file = site_config
    maintest.user_file = user_config

    configuration = __configure(None)
    assert configuration is not None
    assert list(configuration.styles) == ["foo", "bar"]


def test_all_configurations(site_config, user_config, project_config):

    maintest.site_file = site_config
    maintest.user_file = user_config

    configuration = __configure(project_config)
    assert configuration is not None
    assert list(configuration.styles) == ["foo", "bar"]
    assert len(configuration.styles["foo"].list_rules()) == 2
