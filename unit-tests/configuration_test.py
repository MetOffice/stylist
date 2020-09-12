#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""Ensure the configuration module functions as expected."""
from typing import Mapping
from pytest import fixture  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

from stylist.configuration import ConfigurationFile, Configuration


@fixture(scope='module',
         params=({},
                 {'empty-single': {}},
                 {'skinny-single': {'only': 'thing'}},
                 {'fulsome-single': {'first': 'thing',
                                     'second': 'other thing'}},
                 {'first-empty': {},
                  'second-single': {'only': 'one'},
                  'third-full': {'some': 'stuff',
                                 'more': 'stuff'}}))
def case(request: FixtureRequest) -> Mapping[str, Mapping[str, str]]:
    return request.param


class TestConfiguration():
    def test_configuration(self, case) -> None:
        test_unit = Configuration(case)
        assert test_unit.section_names() == list(case.keys())
        for key in case.keys():
            assert test_unit.section(key) == case[key]

    def test_sections_with_prefix(self, case) -> None:
        test_unit = Configuration(case)
        if 'second-single' in case.keys():
            expected = ['second-single']
        else:
            expected = []
        assert test_unit.section_names('second-') == expected


class TestFileConfiguration():
    def test_file_configuration(self, tmp_path, case) -> None:
        config_file = tmp_path / 'test.ini'
        with config_file.open('w') as fhandle:
            for section in case.keys():
                print(f'[{section}]', file=fhandle)
                for key, value in case[section].items():
                    print(f'  {key} = {value}', file=fhandle)
        test_unit = ConfigurationFile(config_file)
        assert test_unit.section_names() == list(case.keys())
        for key in case.keys():
            assert test_unit.section(key) == case[key]
