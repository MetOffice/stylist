#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the 'style' module functions as expected.
"""

import pytest  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

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
        unit_under_test = TestStyle._StyleHarness()
        assert unit_under_test.list_rules() == []

    @pytest.fixture(scope='module',
                    params=[([], []),
                            ([_RuleHarnessOne()], ['_RuleHarnessOne']),
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
        unit_under_test = TestStyle._StyleHarness(*initials[0])
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
        unit_under_test = TestStyle._StyleHarness(rule_one, rule_two)
        reader = SourceStringReader('module foo\nend module foo\n')
        source = FortranSource(reader)
        unit_under_test.check(source)
        assert rule_one.examined == ['module foo\nend module foo\n']
        assert rule_two.examined == ['module foo\nend module foo\n']
