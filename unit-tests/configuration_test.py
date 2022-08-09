#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensure the configuration module functions as expected.
"""
from pathlib import Path
from textwrap import dedent
from typing import Optional, List

from pytest import fixture, raises  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

from stylist import StylistException
from stylist.configuration import load_configuration
from stylist.issue import Issue
from stylist.rule import Rule
from stylist.source import SourceTree, TextProcessor


class DummySource(SourceTree):
    def get_tree(self):
        pass

    def get_tree_error(self) -> Optional[str]:
        pass


class DummyProcOne(TextProcessor):
    def get_text(self) -> str:
        pass


class DummyProcTwo(TextProcessor):
    def get_text(self) -> str:
        pass


class DummyRuleZero(Rule):
    def examine(self, subject) -> List[Issue]:
        pass


class DummyRuleOne(Rule):
    def __init__(self, first):
        self.first = first

    def examine(self, subject) -> List[Issue]:
        pass


class DummyRuleTwo(Rule):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def examine(self, subject) -> List[Issue]:
        pass


class TestConfiguration:
    def test_no_configuration(self, tmp_path: Path):
        config_file = tmp_path / 'no_config.py'
        config_file.write_text(dedent("""
                                      # We import nothing
                                      some_variable = 4
                                      """))
        configuration = load_configuration(config_file)
        assert configuration.file_pipes == {}
        assert configuration.styles == {}

    def test_source_only(self, tmp_path: Path):
        config_file = tmp_path / 'source_only.py'
        config_file.write_text(dedent("""
                                      from stylist.source import FilePipe
                                      from configuration_test import DummySource
                                      foo = FilePipe(DummySource)
                                      """))
        configuration = load_configuration(config_file)
        assert list(configuration.file_pipes.keys()) == ['foo']
        assert configuration.file_pipes['foo'].parser == DummySource
        assert len(configuration.file_pipes['foo'].preprocessors) == 0
        assert configuration.styles == {}

    def test_full_pipe(self, tmp_path: Path):
        config_file = tmp_path / 'full.py'
        config_file.write_text(dedent("""
                                      from stylist.source import FilePipe
                                      from configuration_test import DummyProcOne, DummySource
                                      bar = FilePipe(DummySource, DummyProcOne)
                                      """))
        configuration = load_configuration(config_file)
        assert list(configuration.file_pipes.keys()) == ['bar']
        assert configuration.file_pipes['bar'].parser == DummySource
        assert len(configuration.file_pipes['bar'].preprocessors) == 1
        assert configuration.file_pipes['bar'].preprocessors[0] == DummyProcOne
        assert configuration.styles == {}

    def test_over_full_pipe(self, tmp_path: Path):
        config_file = tmp_path / 'full.py'
        config_file.write_text(dedent("""
                                      from stylist.source import FilePipe
                                      from configuration_test import DummyProcOne, DummyProcTwo, DummySource
                                      baz = FilePipe(DummySource, DummyProcOne, DummyProcTwo)
                                      """))
        configuration = load_configuration(config_file)
        assert list(configuration.file_pipes.keys()) == ['baz']
        assert configuration.file_pipes['baz'].parser == DummySource
        assert len(configuration.file_pipes['baz'].preprocessors) == 2
        assert configuration.file_pipes['baz'].preprocessors[0] == DummyProcOne
        assert configuration.file_pipes['baz'].preprocessors[1] == DummyProcTwo
        assert configuration.styles == {}

    def test_only_rule(self, tmp_path: Path):
        config_file = tmp_path / 'style.py'
        config_file.write_text(dedent("""
                                      from stylist.style import Style
                                      from configuration_test import DummyRuleZero
                                      only_rules = Style(DummyRuleZero())
                                      """))
        configuration = load_configuration(config_file)
        assert configuration.file_pipes == {}
        assert list(configuration.styles.keys()) == ['only_rules']
        assert len(configuration.styles['only_rules'].list_rules()) == 1
        assert isinstance(configuration.styles['only_rules'].list_rules()[0], DummyRuleZero)

    def test_only_multi_rule(self, tmp_path: Path):
        config_file = tmp_path / 'style.py'
        config_file.write_text(dedent("""
                                      from stylist.style import Style
                                      from configuration_test import DummyRuleOne, DummyRuleTwo
                                      only_multi_rules = Style(DummyRuleOne(1), DummyRuleTwo(3, 4))
                                      """))
        configuration = load_configuration(config_file)
        assert configuration.file_pipes == {}
        assert list(configuration.styles.keys()) == ['only_multi_rules']
        assert len(configuration.styles['only_multi_rules'].list_rules()) == 2
        assert isinstance(configuration.styles['only_multi_rules'].list_rules()[0], DummyRuleOne)
        assert configuration.styles['only_multi_rules'].list_rules()[0].first == 1
        assert isinstance(configuration.styles['only_multi_rules'].list_rules()[1], DummyRuleTwo)
        assert configuration.styles['only_multi_rules'].list_rules()[1].first == 3
        assert configuration.styles['only_multi_rules'].list_rules()[1].second == 4

    def test_regex_rule(self, tmp_path: Path):
        config_file = tmp_path / 'regex.py'
        config_file.write_text(dedent("""
                                      from re import compile as recompile
                                      from stylist.style import Style
                                      from configuration_test import DummyRuleOne
                                      regex_rule = Style(DummyRuleOne(recompile(r'.*')))
                                      """))
        configuration = load_configuration(config_file)
        assert configuration.file_pipes == {}
        assert list(configuration.styles.keys()) == ['regex_rule']
        assert len(configuration.styles['regex_rule'].list_rules()) == 1
        assert isinstance(configuration.styles['regex_rule'].list_rules()[0], DummyRuleOne)
        assert configuration.styles['regex_rule'].list_rules()[0].first.pattern == r'.*'
