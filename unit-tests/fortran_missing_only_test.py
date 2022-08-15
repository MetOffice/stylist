#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Test of the rule for missing "only" clauses.
"""
from typing import List, Optional, Tuple

import pytest  # type: ignore

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


class TestMissingOnly(object):
    """
    Tests the checker of missing "use" clauses.
    """
    @pytest.fixture(scope='class',
                    params=['program', 'module'])
    def unit_type(self, request):
        """
        Parameter fixture giving program unit types.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=[[], ['missing_mod']])
    def ignorance(self, request):
        """
        Parameter fixture giving ignore lists.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=[[(None, [])],
                            [('missing_mod', [])],
                            [('present_mod', ['stuff'])],
                            [('multi_mod', ['one', 'two'])],
                            [('missing_mod', []), ('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']), ('missing_mod', [])]])
    def unit_usage(self, request):
        """
        Parameter fixture giving permutations of "use" statements.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=[[(None, [])],
                            [('missing_mod', [])],
                            [('present_mod', ['stuff'])],
                            [('multi_mod', ['one', 'two'])],
                            [('missing_mod', []), ('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']), ('missing_mod', [])]])
    def procedure_usage(self, request):
        """
        Parameter fixture giving permutations of "use" statements.
        """
        return request.param

    def test_use(self,
                 unit_type: str,
                 unit_usage: List[Tuple[Optional[str], List[str]]],
                 procedure_usage: List[Tuple[Optional[str], List[str]]],
                 ignorance: List[str]) -> None:
        """
        Checks that the rule reports missing "use" clauses correctly.
        """
        def prepare(line_number: int,
                    params: List[Tuple[Optional[str], List[str]]]) \
                -> Tuple[List[str], List[str], int]:
            usage: List[str] = []
            expectations: List[str] = []
            for details in params:
                line = None
                if details[0] is not None:
                    line = 'use {0}'.format(details[0])
                    if details[1]:
                        line += ', only : {0}'.format(', '.join(details[1]))
                        line_number += 1
                    elif details[0] not in ignorance:
                        message = f'{line_number}: Usage of "{details[0]}" ' \
                                  f'without "only" clause.'
                        expectations.append(message)
                        line_number += 1
                if line:
                    usage.append(line)
            return usage, expectations, line_number

        text = '''{type} test
                   {uusage}
                   implicit none
                 contains
                   subroutine foo()
                     {pusage}
                     implicit none
                   end subroutine foo
                 end {type} test
               '''

        unit_lines, unit_expects, last_line = prepare(2, unit_usage)
        if len(unit_lines) == 0:
            last_line += 1
        proc_lines, proc_expects, _ = prepare(last_line + 3, procedure_usage)
        reader = SourceStringReader(text.format(type=unit_type,
                                                uusage='\n'.join(unit_lines),
                                                pusage='\n'.join(proc_lines)))
        source = FortranSource(reader)

        expectation = list(unit_expects)
        expectation.extend(proc_expects)
        print(text.format(type=unit_type,
                          uusage='\n'.join(unit_lines),
                          pusage='\n'.join(proc_lines)))
        print(expectation)
        if ignorance:
            unit_under_test = stylist.fortran.MissingOnly(ignore=ignorance)
        else:
            unit_under_test = stylist.fortran.MissingOnly()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
