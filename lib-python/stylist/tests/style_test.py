#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Ensures the 'style' module functions as expected.
'''
from __future__ import absolute_import, division, print_function

import stylist.rule
from stylist.source import FortranSource, SourceStringReader
import stylist.style
import pytest


class TestStyle(object):
    '''
    Tests the abstract TestStyle class.
    '''
    class _StyleHarness(stylist.style.Style):
        '''
        Null but concrete implementation of abstract class.
        '''
        pass

    def test_constructor_empty(self):
        # pylint: disable=no-self-use
        '''
        Checks that constructing an empty rule set works.
        '''
        unit_under_test = TestStyle._StyleHarness([])
        assert unit_under_test.list_rules() == []

    class _RuleHarnessOne(stylist.rule.Rule):
        '''
        Completely empty but concrete implementatino of a rule.
        '''
        # pylint: disable=too-few-public-methods
        def examine(self, subject):
            pass

    class _RuleHarnessTwo(stylist.rule.Rule):
        # pylint: disable=too-few-public-methods
        def examine(self, subject):
            pass

    @pytest.fixture(scope='module',
                    params=[([], []),
                            (_RuleHarnessOne(), ['_RuleHarnessOne']),
                            ([_RuleHarnessOne()], ['_RuleHarnessOne']),
                            ([_RuleHarnessTwo(), _RuleHarnessOne()],
                             ['_RuleHarnessTwo', '_RuleHarnessOne'])])
    def initials(self, request):
        # pylint: disable=no-self-use
        '''
        Parameter fixture giving initial lists and expected lists.
        '''
        yield request.param

    def test_constructor(self, initials):
        # pylint: disable=no-self-use
        '''
        Checks that various permutations of rules are correctly lodged in the
        style.
        '''
        unit_under_test = TestStyle._StyleHarness(initials[0])
        assert unit_under_test.list_rules() == initials[1]

    class _RuleHarness(stylist.rule.Rule):
        # pylint: disable=too-few-public-methods
        def __init__(self):
            self.examined = []

        def examine(self, subject):
            self.examined.append(subject.get_text())
            return []

    def test_examination(self):
        # pylint: disable=no-self-use
        '''
        Checks that all the rules in a style get a look at the program.
        '''
        rule_one = TestStyle._RuleHarness()
        rule_two = TestStyle._RuleHarness()
        unit_under_test = TestStyle._StyleHarness([rule_one, rule_two])
        reader = SourceStringReader('module foo\nend module foo\n')
        source = FortranSource(reader)
        unit_under_test.check(source)
        assert rule_one.examined == ['module foo\nend module foo\n']
        assert rule_two.examined == ['module foo\nend module foo\n']


class TestLFRicStyle(object):
    # pylint: disable=too-few-public-methods
    '''
    Tests the LFRicStyle class.
    '''
    def test_rules(self):
        # pylint: disable=no-self-use
        '''
        Checks that the style contains the correct rules.
        '''
        unit_under_test = stylist.style.LFRicStyle()

        assert unit_under_test.list_rules() == ['FortranCharacterset',
                                                'TrailingWhitespace',
                                                'MissingImplicit',
                                                'MissingOnly']
