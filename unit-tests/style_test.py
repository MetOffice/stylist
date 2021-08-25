#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the 'style' module functions as expected.
"""
from pathlib import Path
from typing import cast, List

import pytest  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

from stylist import StylistException
from stylist.configuration import Configuration
import stylist.fortran
import stylist.rule
from stylist.source import FortranSource, SourceStringReader
import stylist.style


class _RuleHarnessOne(stylist.rule.Rule):
    """
    Completely empty but concrete implementation of a rule.
    """

    def examine(self, subject):
        pass


class _RuleHarnessTwo(stylist.rule.Rule):
    """
    Completely empty but concrete implementation of a rule. This one has a
    constructor.
    """
    def __init__(self, thing):
        self.thing = thing

    def examine(self, subject):
        pass


class TestStyle(object):
    """
    Tests the abstract TestStyle class.
    """
    class _StyleHarness(stylist.style.Style):
        """
        Null but concrete implementation of abstract class.
        """
        pass

    def test_constructor_empty(self):
        """
        Checks that constructing an empty rule set works.
        """
        unit_under_test = TestStyle._StyleHarness([])
        assert unit_under_test.list_rules() == []

    @pytest.fixture(scope='module',
                    params=[([], []),
                            (_RuleHarnessOne(), ['_RuleHarnessOne']),
                            ([_RuleHarnessOne()], ['_RuleHarnessOne']),
                            ([_RuleHarnessTwo('blah'), _RuleHarnessOne()],
                             ['_RuleHarnessTwo', '_RuleHarnessOne'])])
    def initials(self, request: FixtureRequest):
        """
        Parameter fixture giving initial lists and expected lists.
        """
        yield request.param

    def test_constructor(self, initials):
        """
        Checks that various permutations of rules are correctly lodged in the
        style.
        """
        unit_under_test = TestStyle._StyleHarness(initials[0])
        assert [rule.__class__.__name__
                for rule in unit_under_test.list_rules()] == initials[1]

    class _RuleHarness(stylist.rule.Rule):
        def __init__(self):
            self.examined = []

        def examine(self, subject):
            self.examined.append(subject.get_text())
            return []

    def test_examination(self):
        """
        Checks that all the rules in a style get a look at the program.
        """
        rule_one = TestStyle._RuleHarness()
        rule_two = TestStyle._RuleHarness()
        unit_under_test = TestStyle._StyleHarness([rule_one, rule_two])
        reader = SourceStringReader('module foo\nend module foo\n')
        source = FortranSource(reader)
        unit_under_test.check(source)
        assert rule_one.examined == ['module foo\nend module foo\n']
        assert rule_two.examined == ['module foo\nend module foo\n']


class TestDetermineStyle:
    """
    Ensures a style can be read from a configuration structure.
    """
    @staticmethod
    def _name_rules(style: stylist.style.Style) -> List[str]:
        """
        Converts a style into a list of rule names.
        """
        return [rule.__class__.__name__ for rule in style.list_rules()]

    def test_none(self):
        """
        Checks that an error is thrown if an attempt is made to get a style
        from configuration which contains none.
        """
        no_style_conf = Configuration({'': {'a': 42}})
        with pytest.raises(StylistException):
            stylist.style.determine_style(no_style_conf, 'wibble')

    def test_one_of_several(self, tmp_path: Path):
        """
        Checks that a single style can be extracted from several alternatives.
        """
        several_style_conf = Configuration(
            {'style.the_first': {'rules': '_RuleHarnessOne'},
             'style.the_second': {'rules':
                                  '_RuleHarnessOne, _RuleHarnessTwo(42)'},
             'beef': {'whatsits': 'cheesy'},
             'style.the_third': {'rules': "_RuleHarnessTwo('super')"}})
        new_style = stylist.style.determine_style(several_style_conf,
                                                  'the_second')
        assert self._name_rules(new_style) == ['_RuleHarnessOne',
                                               '_RuleHarnessTwo']

    def test_single_style(self, tmp_path: Path):
        """
        Checks that a single style can be extracted from a list of one.
        """
        single_style_conf = Configuration(
            {'cheese': {'thingy': 'thangy'},
             'style.singular': {'rules':
                                "_RuleHarnessOne, _RuleHarnessTwo('blah')"}})
        new_style = stylist.style.determine_style(single_style_conf,
                                                  'singular')
        assert self._name_rules(new_style) == ['_RuleHarnessOne',
                                               '_RuleHarnessTwo']

    def test_default_style(self, tmp_path: Path):
        """
        Checks that the only style is loaded if none is specified.
        """
        single_style_conf = Configuration(
            {'cheese': {'thingy': 'thangy'},
             'style.maybe': {'rules':
                             "_RuleHarnessOne, _RuleHarnessTwo('blah')"}})
        new_style = stylist.style.determine_style(single_style_conf)
        assert self._name_rules(new_style) == ['_RuleHarnessOne',
                                               '_RuleHarnessTwo']

    def test_no_default(self, tmp_path: Path):
        """
        Checks that an error is thrown if an attempt is made to load a default
        style from an empty style list.
        """
        empty_conf = Configuration({'cheese': {'a': '42'}})
        with pytest.raises(StylistException):
            stylist.style.determine_style(empty_conf)

    def test_ambiguous_default(self, tmp_path: Path):
        """
        Checks that an error is thrown if no style is specified but several
        are available.
        """
        several_style_conf = Configuration(
            {'style.the_first': {'rules': '_RuleHarnessOne'},
             'style.the_second': {'rules':
                                  '_RuleHarnessOne, _RuleHarnessTwo(42)'},
             'beef': {'whatsits': 'cheesy'},
             'style.the_third': {'rules': "_RuleHarnessTwo('super')"}})
        with pytest.raises(StylistException):
            stylist.style.determine_style(several_style_conf)

    def test_raw_argument(self, tmp_path: Path):
        """
        Checks that raw-string arguments are handled correctly.
        """
        initialiser = {'style.rawarg': {'rules': "_RuleHarnessTwo(r'.*')"}}
        conf = Configuration(initialiser)
        style = stylist.style.determine_style(conf)

        rules = style.list_rules()
        assert len(rules) == 1
        assert isinstance(rules[0], _RuleHarnessTwo)
        assert cast(_RuleHarnessTwo, rules[0]).thing == r'.*'

    def test_keyword_argument(self, tmp_path: Path):
        """
        Checks that keyword arguments are handled correctly.
        """
        initialiser = {'style.rawarg': {'rules': "_RuleHarnessTwo(thing='bing')"}}
        conf = Configuration(initialiser)
        style = stylist.style.determine_style(conf)

        rules = style.list_rules()
        assert len(rules) == 1
        assert isinstance(rules[0], _RuleHarnessTwo)
        assert cast(_RuleHarnessTwo, rules[0]).thing == 'bing'
