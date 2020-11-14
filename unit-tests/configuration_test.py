#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""Ensure the configuration module functions as expected."""
from typing import Mapping
from pytest import fixture, raises  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

from stylist import StylistException
from stylist.configuration import ConfigurationFile, Configuration


@fixture(scope='module',
         params=({'style.only-rules': {'rules': 'foo-rule'}},
                 {'style.only-multi-rules': {'rules': 'teapot-rule, cheese-rule'}},
                 {'style.plus-rules': {'rules': 'bar-rule',
                                       'second': 'other thing'}}))
def case(request: FixtureRequest) -> Mapping[str, Mapping[str, str]]:
    return request.param


class TestConfiguration():
    def test_configuration(self, case) -> None:
        test_unit = Configuration(case)
        expected = [key[6:] for key in case.keys() if key.startswith('style.')]
        assert test_unit.available_styles() == expected
        for key in case.keys():
            if key.startswith('style.'):
                assert test_unit.get_style(key[6:]) == case[key]['rules'].split(',')

    def test_empty_file(self) -> None:
        test_unit = Configuration({})
        assert test_unit.available_styles() == []

    def test_no_styles(self) -> None:
        test_unit = Configuration({'no-style': {}})
        assert test_unit.available_styles() == []

    def test_empty_style(self) -> None:
        test_unit = Configuration({'style.empty': {}})
        assert test_unit.available_styles() == ['empty']
        with raises(KeyError):
            _ = test_unit.get_style('empty')

    def test_style_without_rules(self) -> None:
        test_unit = Configuration({'style.no-rules': {'only': 'thing'}})
        assert test_unit.available_styles() == ['no-rules']
        with raises(KeyError):
            _ = test_unit.get_style('no-rules')

    def test_style_with_empty_rules(self) -> None:
        test_unit = Configuration({'style.empty-rules': {'rules': ''}})
        assert test_unit.available_styles() == ['empty-rules']
        with raises(StylistException):
            _ = test_unit.get_style('empty-rules')


class TestFileConfiguration():
    def test_file_configuration(self, tmp_path, case) -> None:
        config_file = tmp_path / 'test.ini'
        with config_file.open('w') as fhandle:
            for section in case.keys():
                print(f'[{section}]', file=fhandle)
                for key, value in case[section].items():
                    if isinstance(value, list):
                        print(f'  {key} = {", ".join(value)}', file=fhandle)
                    else:
                        print(f'  {key} = {value}', file=fhandle)
        test_unit = ConfigurationFile(config_file)
        assert test_unit.available_styles() \
               == [key[6:] for key in case.keys()]
        for key in case.keys():
            style_name = key[6:]
            if 'rules' in case[key]:
                assert test_unit.get_style(style_name) == case[key]['rules'].split(',')
            else:
                with raises(KeyError):
                    _ = test_unit.get_style(style_name)
