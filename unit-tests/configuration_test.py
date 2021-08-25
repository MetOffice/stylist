#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""Ensure the configuration module functions as expected."""
import re
from typing import Mapping, Optional, Sequence, Tuple, Type
from pytest import fixture, raises  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

from stylist import StylistException
from stylist.configuration import ConfigurationFile, Configuration
from stylist.source import (CPreProcessor,
                            CSource,
                            FortranPreProcessor,
                            FortranSource,
                            PFUnitProcessor,
                            SourceTree,
                            TextProcessor)


@fixture(scope='module',
         params=((None, None),
                 ('boo:fortran', ('boo', FortranSource, [])),
                 ('coo:c:cpp', ('coo', CSource, [CPreProcessor])),
                 ('doo:fortran:pfp:fpp', ('doo',
                                          FortranSource,
                                          [PFUnitProcessor,
                                           FortranPreProcessor]))))
def pipe_string(request: FixtureRequest) \
    -> Tuple[str, Optional[Tuple[str,
                                 Type[SourceTree],
                                 Sequence[Type[TextProcessor]]]]]:
    return request.param


@fixture(scope='module',
         params=({'style.only-rules': {'rules': 'foo-rule'}},
                 {'style.only-multi-rules': {'rules':
                                             'teapot-rule, cheese-rule'}},
                 {'style.plus-rules': {'rules': 'bar-rule',
                                       'second': 'other thing'}},
                 {'style.arg-rule': {'rules': 'arg-rule(this)'}},
                 {'style.args-rule': {'rules': 'args-rule(this, that)'}},
                 {'style.args-rules': {
                     'rules': 'beef-rule(dee, dum), fish_rule(sam, del)'}}))
def style_file(request: FixtureRequest) -> Mapping[str, Mapping[str, str]]:
    return request.param


_RULE_PATTERN = re.compile(r'[^,(]+(?:\(.+?\))?')


class TestConfiguration():
    def test_configuration(self, style_file) -> None:
        test_unit = Configuration(style_file)
        expected = [key[6:] for key in style_file.keys()
                    if key.startswith('style.')]
        assert test_unit.available_styles() == expected
        for key in style_file.keys():
            if key.startswith('style.'):
                expected = _RULE_PATTERN.findall(style_file[key]['rules'])
                expected = [item.strip() for item in expected]
                assert test_unit.get_style(key[6:]) == expected

    def test_raw_rule_arguments(self) -> None:
        initialiser = {'style.raw-args': {'rules': 'rule(r\'.*\')'}}
        test_unit = Configuration(initialiser)
        assert test_unit.available_styles() == ['raw-args']
        assert test_unit.get_style('raw-args') == ['rule(r\'.*\')']

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

    def test_parse_pipe(self, pipe_string) -> None:
        stimulus, expected = pipe_string
        if expected is not None:
            extension, source, preproc \
                = Configuration.parse_pipe_description(stimulus)
            assert expected[0] == extension
            assert expected[1] == source
            assert expected[2] == preproc
        else:
            with raises(StylistException):
                _ = Configuration.parse_pipe_description(stimulus)

    def test_no_pipe(self) -> None:
        test_unit = Configuration({})
        assert [] == test_unit.get_file_pipes()

    def test_get_pipe(self) -> None:
        input = {'file-pipe': {'f90': 'fortran',
                               'F90': 'fortran:fpp',
                               'x90': 'fortran:pfp:fpp'}}
        expected = [('f90', FortranSource, []),
                    ('F90', FortranSource, [FortranPreProcessor]),
                    ('x90', FortranSource, [PFUnitProcessor,
                                            FortranPreProcessor])]
        test_unit = Configuration(input)
        assert expected == list(test_unit.get_file_pipes())


class TestFileConfiguration:
    def test_file_configuration(self, tmp_path, style_file) -> None:
        config_file = tmp_path / 'test.ini'
        with config_file.open('w') as fhandle:
            for section in style_file.keys():
                print(f'[{section}]', file=fhandle)
                for key, value in style_file[section].items():
                    if isinstance(value, list):
                        print(f'  {key} = {", ".join(value)}', file=fhandle)
                    else:
                        print(f'  {key} = {value}', file=fhandle)
        test_unit = ConfigurationFile(config_file)
        assert test_unit.available_styles() \
            == [key[6:] for key in style_file.keys()]
        for key in style_file.keys():
            style_name = key[6:]
            if 'rules' in style_file[key]:
                expected = _RULE_PATTERN.findall(style_file[key]['rules'])
                expected = [item.strip() for item in expected]
                assert test_unit.get_style(style_name) == expected
            else:
                with raises(KeyError):
                    _ = test_unit.get_style(style_name)
