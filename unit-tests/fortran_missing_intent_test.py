#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the rule for missing intents on dummy arguments.
"""
import pytest  # type: ignore

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.


@pytest.fixture(scope='module',
                params=['''program test_program
                            contains
                            {procedure}
                            end program test_program''',
                        '''module test_module
                            contains
                            {procedure}
                            end module test_module''',
                        '''! Pad to third line to save calculating line numbers
                           !
                           {procedure}'''])
def parent_container(request):
    """
    Parameter fixture giving possible parent containers of functions ond
    subroutines
    """
    return request.param


@pytest.fixture(scope='module',
                params=[('''subroutine test_subroutine({dummy_args})
                            {type_declaration}
                            end subroutine test_subroutine''', 'subroutine'),
                        ('''subroutine test_subroutine({dummy_args})
                            end subroutine test_subroutine''', 'subroutine'),
                        ('''function test_function({dummy_args})
                            {type_declaration}
                            end function test_function''', 'function'),
                        ('''function test_function({dummy_args})
                            end function test_function''', 'function'),
                        ])
def procedure(request):
    """
    Parameter fixture giving subprograms and their type
    """
    return request.param[0], request.param[1]


@pytest.fixture(scope='module',
                params=[(['foo'], 'integer {intent} :: foo'),
                        (['foo', 'bar'], 'integer {intent} :: foo, bar'),
                        (['foo'], 'integer, pointer {intent} :: foo(5)'),
                        ([], 'integer{intent} :: foo'),
                        (['Foo'], 'integer{intent} :: FOO')
                        ])
def arguments(request):
    """
    Parameter fixture giving dummy arguments and type declarations
    """
    return request.param[0], request.param[1]


@pytest.fixture(scope='module',
                params=['intent(in)', 'intent(out)', 'intent(inout)', ''])
def intent(request):
    """
    Parameter fixture giving possible intents. Some permutations produce
    invalid fortran, e.g. two or no intent out arguments on a function.
    This simplifies the test's logic, and is not a problem as the compiler
    will pick up any such issues.
    """
    return request.param


class TestMissingIntent(object):
    """
    Tests the checker of missing intent statements.
    """

    def test_intent(self, parent_container, procedure, arguments, intent) \
            -> None:
        """
        Checks all permutations.
        """

        text = parent_container.format(procedure=procedure[0])
        text = text.format(
            dummy_args=','.join([x.lower() for x in arguments[0]]),
            type_declaration=arguments[1])

        if intent != '':
            intent_str = ', ' + intent
        else:
            intent_str = intent

        text = text.format(intent=intent_str)

        print(text)

        expectation = []
        issue_base = '{line}: Dummy argument "{arg}" of {unit_type} "{unit}" '\
                     'is missing an "intent" statement'
        for arg in arguments[0]:
            if intent == '' or 'type_declaration' not in procedure[0]:
                expectation.append(issue_base.format(line=3, arg=arg.lower(),
                                                     unit_type=procedure[1],
                                                     unit='test_' + procedure[
                                                         1]))

        reader = SourceStringReader(text)
        source = FortranSource(reader)
        unit_under_test = stylist.fortran.MissingIntent()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]

        assert issue_descriptions == expectation
