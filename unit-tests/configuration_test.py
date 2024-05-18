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
from typing import cast, Optional, List

from stylist.configuration import load_configuration
from stylist.issue import Issue
from stylist.rule import Rule
from stylist.source import SourceTree, TextProcessor


class DummySource(SourceTree):
    @staticmethod
    def get_name() -> str:
        return "Dummy source"

    def get_tree(self):
        pass

    def get_tree_error(self) -> Optional[str]:
        pass


class DummyProcOne(TextProcessor):
    @staticmethod
    def get_name() -> str:
        return "Dummy processor one"

    def get_text(self) -> str:
        return "dummy text one"


class DummyProcTwo(TextProcessor):
    @staticmethod
    def get_name() -> str:
        return "Dummy processor two"

    def get_text(self) -> str:
        return "dummy text two"


class DummyRuleZero(Rule):
    def examine(self, subject) -> List[Issue]:
        return []


class DummyRuleOne(Rule):
    def __init__(self, first):
        self.first = first

    def examine(self, subject) -> List[Issue]:
        return []


class DummyRuleTwo(Rule):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def examine(self, subject) -> List[Issue]:
        return []


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
        style = configuration.file_pipes['foo']
        assert style.parser == DummySource
        assert len(style.preprocessors) == 0
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
        style = configuration.file_pipes['bar']
        assert style.parser == DummySource
        assert len(style.preprocessors) == 1
        assert style.preprocessors[0] == DummyProcOne
        assert configuration.styles == {}

    def test_over_full_pipe(self, tmp_path: Path):
        config_file = tmp_path / 'full.py'
        config_file.write_text(dedent("""
            from stylist.source import FilePipe
            from configuration_test import (DummyProcOne,
                                            DummyProcTwo,
                                            DummySource)
            baz = FilePipe(DummySource, DummyProcOne, DummyProcTwo)
            """))
        configuration = load_configuration(config_file)
        assert list(configuration.file_pipes.keys()) == ['baz']
        style = configuration.file_pipes['baz']
        assert style.parser == DummySource
        assert len(style.preprocessors) == 2
        assert style.preprocessors[0] == DummyProcOne
        assert style.preprocessors[1] == DummyProcTwo
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
        style = configuration.styles['only_rules']
        assert style.name == "only_rules"
        assert len(style.list_rules()) == 1
        assert isinstance(style.list_rules()[0], DummyRuleZero)

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
        style = configuration.styles['only_multi_rules']
        assert style.name == "only_multi_rules"
        assert len(style.list_rules()) == 2
        assert isinstance(style.list_rules()[0], DummyRuleOne)
        assert cast(DummyRuleOne, style.list_rules()[0]).first == 1
        assert isinstance(style.list_rules()[1], DummyRuleTwo)
        assert cast(DummyRuleTwo, style.list_rules()[1]).first == 3
        assert cast(DummyRuleTwo, style.list_rules()[1]).second == 4

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
        style = configuration.styles['regex_rule']
        assert style.name == "regex_rule"
        assert len(style.list_rules()) == 1
        assert isinstance(style.list_rules()[0], DummyRuleOne)
        assert cast(DummyRuleOne, style.list_rules()[0]).first.pattern == r'.*'

    def test_config_add_pipes(self, tmp_path: Path):
        first_file = tmp_path / 'first.py'
        first_file.write_text(dedent("""
            from stylist.source import FilePipe
            from configuration_test import DummySource
            foo = FilePipe(DummySource)
            """))

        second_file = tmp_path / 'second.py'
        second_file.write_text(dedent("""
            from stylist.source import FilePipe
            from configuration_test import DummyProcOne, DummySource
            foo = FilePipe(DummySource, DummyProcOne)
            """))

        configuration = load_configuration(first_file)
        assert list(configuration.file_pipes.keys()) == ['foo']
        style = configuration.file_pipes['foo']
        assert style.parser == DummySource
        assert len(style.preprocessors) == 0
        assert configuration.styles == {}

        configuration.overload(load_configuration(second_file))
        assert list(configuration.file_pipes.keys()) == ['foo']
        style = configuration.file_pipes['foo']
        assert style.parser == DummySource
        assert len(style.preprocessors) == 1
        assert configuration.styles == {}

    def test_config_add_styles(self, tmp_path: Path):
        first_file = tmp_path / 'first.py'
        first_file.write_text(dedent("""
            from stylist.style import Style
            from configuration_test import DummyRuleZero
            foo = Style(DummyRuleZero())
            """))

        second_file = tmp_path / 'second.py'
        second_file.write_text(dedent("""
            from stylist.style import Style
            from configuration_test import DummyRuleOne
            foo = Style(DummyRuleOne(1))
            """))

        configuration = load_configuration(first_file)
        assert list(configuration.styles.keys()) == ['foo']
        style = configuration.styles['foo']
        assert isinstance(style.list_rules()[0], DummyRuleZero)

        configuration.overload(load_configuration(second_file))
        assert list(configuration.styles.keys()) == ['foo']
        style = configuration.styles['foo']
        assert isinstance(style.list_rules()[0], DummyRuleOne)
