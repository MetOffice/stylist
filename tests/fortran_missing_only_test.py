#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Test of the rule for missing "only" clauses.
'''

import pytest
import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


class TestMissingOnly(object):
    '''
    Tests the checker of missing "use" clauses.
    '''
    @pytest.fixture(scope='class',
                    params=['program', 'module'])
    def unit_type(self, request):
        '''
        Parameter fixture giving program unit types.
        '''
        # pylint: disable=no-self-use
        yield request.param

    @pytest.fixture(scope='class',
                    params=[[], ['missing_mod']])
    def ignorance(self, request):
        '''
        Parameter fixture giving ignore lists.
        '''
        # pylint: disable=no-self-use
        yield request.param

    @pytest.fixture(scope='class',
                    params=[[(None, [])],
                            [('missing_mod', [])],
                            [('present_mod', ['stuff'])],
                            [('multi_mod', ['one', 'two'])],
                            [('missing_mod', []), ('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']), ('missing_mod', [])]])
    def unit_usage(self, request):
        '''
        Parameter fixture giving permutations of "use" statements.
        '''
        # pylint: disable=no-self-use
        yield request.param

    @pytest.fixture(scope='class',
                    params=[[(None, [])],
                            [('missing_mod', [])],
                            [('present_mod', ['stuff'])],
                            [('multi_mod', ['one', 'two'])],
                            [('missing_mod', []), ('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']), ('missing_mod', [])]])
    def procedure_usage(self, request):
        '''
        Parameter fixture giving permutations of "use" statements.
        '''
        # pylint: disable=no-self-use
        yield request.param

    def test_use(self, unit_type, unit_usage, procedure_usage, ignorance):
        '''
        Checks that the rule reports missing "use" clauses correctly.
        '''
        # pylint: disable=no-self-use
        def prepare(params):
            usage = []
            expectations = []
            for details in params:
                line = None
                if details[0] is not None:
                    line = 'use {0}'.format(details[0])
                    if details[1]:
                        line += ', only : {0}'.format(', '.join(details[1]))
                    elif details[0] not in ignorance:
                        message = 'Usage of "{0}" without "only" clause.'
                        expectations.append(message.format(details[0]))
                if line:
                    usage.append(line)
            return usage, expectations

        unit_lines, unit_expects = prepare(unit_usage)
        proc_lines, proc_expects = prepare(procedure_usage)
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
        reader = SourceStringReader(text.format(type=unit_type,
                                                uusage='\n'.join(unit_lines),
                                                pusage='\n'.join(proc_lines)))
        source = FortranSource(reader)

        expectation = list(unit_expects)
        expectation.extend(proc_expects)

        if ignorance:
            unit_under_test = stylist.fortran.MissingOnly(ignore=ignorance)
        else:
            unit_under_test = stylist.fortran.MissingOnly()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
