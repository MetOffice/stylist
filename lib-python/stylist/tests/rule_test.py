#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Tests of the stylist.rule module.
'''
from __future__ import absolute_import, division, print_function

import fparser.two.Fortran2003
import stylist.rule
from stylist.source import FortranSource, SourceStringReader
import pytest


class TestFortranCharacterset(object):
    '''
    Tests the rule which ensures none Fortran characters do not appear in the
    source.
    '''
    _SIMPLE_NO_PROBLEMS = '''
                          program immaculate

                            use iso_fortran_env, only : output_unit

                            implicit none

                            ! There are no character set errors here

                            write( output_unit, '("Cheese and ", A)' ) "Beef"

                          end program immaculate
                          '''
    _SIMPLE_TAB = '''
                  program tab_mistake

                    implicit none

                    write(6, '(A)')	'Hello'

                  end program tab_mistake
                  '''
    _SIMPLE_COMMENT = '''
                      program exotic_comment

                        implicit none

                        ! Comments may have	exotics

                      end program exotic_comment
                      '''
    _SIMPLE_STRINGS = '''
                      program exotic_strings

                        implicit none

                        write(6, '(A)') 'First	string'
                        write(6,'(A)') "Second	string"

                      end program exotic_strings
                      '''
    _SIMPLE_FORMAT = '''
                     program exotic_format

                       implicit none

                       write(6,'("This	thing: ", I0)') 4

                     end program exotic_format
                     '''

    @pytest.fixture(scope='class',
                    params=[(_SIMPLE_NO_PROBLEMS, []),
                            (_SIMPLE_TAB,
                             ["6: Found character '\\t' not in "
                              + "Fortran character set"]),
                            (_SIMPLE_COMMENT, []),
                            (_SIMPLE_STRINGS, []),
                            (_SIMPLE_FORMAT, [])])
    def simple_source(self, request):
        '''
        Parameter fixture giving a simple Fortran source with various
        caracterset issues.
        '''
        # pylint: disable=no-self-use
        yield request.param

    def test_simple(self, simple_source):
        # pylint: disable=no-self-use
        '''
        Ensures a given input source generates the correct issue list.
        '''
        unit_under_test = stylist.rule.FortranCharacterset()
        reader = SourceStringReader(simple_source[0])
        source = FortranSource(reader)
        issues = unit_under_test.examine(source)
        assert [str(issue) for issue in issues] == simple_source[1]


_NO_TWS = '''
program no_trailing_whitespace

  use iso_fortran_env, only : output_unit

  implicit none

  write( output_unit, '("Hello ", A)' ) 'world'

end program no_trailing_whitespace
'''

_SOME_TWS = '''
program some_trailing_whitespace

  use iso_fortran_env, only : output_unit

  implicit none 

  write( output_unit, '("Hello ", A)' ) 'world'
  
end program some_trailing_whitespace
'''

_PF_TWS = '''module trailing_whitespace_in_unit_tests

  use pFUnit_mod

  implicit none 

  @TestCase
  type, extends(TestCase) :: ThisTest
  contains
    procedure :: test_thing
  end type ThisTest

contains

  @test
  subroutine test_thing( this )

    implicit none

    class(ThisTest), intent(inout) :: this
 
  end subroutine test_thing

end module trailing_whitespace_in_unit_tests'''

class TestTrailingWhitespace(object):
    '''
    Tests the checker of trailing whitespace.
    '''
    @pytest.fixture(scope='class',
                    params=[(_NO_TWS, []),
                            (_SOME_TWS, [6, 9]),
                            (_PF_TWS, [5, 21])])
    def example_source(self, request):
        # pylint: disable=no-self-use
        '''
        Parameter fixture giving Fortran source with various
        trailing whitespace issues.
        '''
        yield request.param

    def test_examples(self, example_source):
        '''
        Ensures trailing whitespace is detected on the correct lines.
        '''
        unit_under_test = stylist.rule.TrailingWhitespace()
        reader = SourceStringReader(example_source[0])
        source = FortranSource(reader)
        issues = unit_under_test.examine(source)
        assert [str(issue) for issue in issues] \
               == [str(eln) + ': Found trailing white space'
                   for eln in example_source[1]]


class TestMissingImplicit(object):
    '''
    Tests the checker of missing implicit statements.
    '''
    @pytest.fixture
    def simple_source(self):
        '''
        Parameter fixture giving a simple Fortran source example.
        '''
        # pylint: disable=no-self-use
        source = '''
                program fred
                    use iso_fortran_env, only : output_unit
                    implicit none
                    call greeting()
                    call farwell()
                contains
                    subroutine greeting()
                    write(output_unit,'("Hello world")')
                    end subroutine greeting
                    subroutine farewell()
                    write(output_unit, '("Good bye")')
                    end subroutine farewell
                end program fred
                '''
        reader = fparser.common.readfortran.FortranStringReader(source)
        return fparser.two.Fortran2003.Program(reader)

    @pytest.fixture(scope='class',
                    params=[('''program barney
                                implicit none
                                write(6, '("boo")')
                                end program barney''', []),
                            ('''program wilma
                                write(6, '("boo")')
                                end program wilma''',
                             ["Program 'wilma' is missing an "
                              + "implicit statement"]),
                            ('''module betty
                                implicit none
                                end module betty''', []),
                            ('''module pebbles
                                end module pebbles''',
                             ["Module 'pebbles' is missing an "
                              + "implicit statement"]),
                            ('''function bammbamm()
                                implicit none
                                character(3) :: bammbamm
                                bammbamm = 'boo'
                                end function bammbamm''', []),
                            ('''function dino()
                                character(3) :: dino
                                dino = 'boo'
                                end function dino''',
                             ["Function 'dino' is missing an "
                              + "implicit statement"]),
                            ('''subroutine hoppy()
                                implicit none
                                write(6, '("boo")')
                                end subroutine hoppy''', []),
                            ('''subroutine baby_puss()
                                write(6, '("boo")')
                                end subroutine baby_puss''',
                             ["Subroutine 'baby_puss' is missing an "
                              + "implicit statement"])])
    def empty_program_unit_implicit(self, request):
        '''
        Parameter fixture giving permutations of program unit with and without
        "implicit none".
        '''
        # pylint: disable=no-self-use
        yield request.param[0], request.param[1]

    def test_implicit(self, empty_program_unit_implicit):
        # pylint: disable=no-self-use
        '''
        Checks all permutations of program units.
        '''
        reader = SourceStringReader(empty_program_unit_implicit[0])
        source = FortranSource(reader)

        expectation = empty_program_unit_implicit[1]

        unit_under_test = stylist.rule.MissingImplicit('none')
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation

    @pytest.fixture(scope='class',
                    params=[('''program barney
                                implicit none
                                write(6, '("boo")')
                                contains
                                {procedure}
                                end program barney''', []),
                            ('''program wilma
                                write(6, '("boo")')
                                contains
                                {procedure}
                                end program wilma''',
                             ["Program 'wilma' is missing "
                              + "an implicit statement"]),
                            ('''module betty
                                implicit none
                                contains
                                {procedure}
                                end module betty''', []),
                            ('''module pebbles
                                contains
                                {procedure}
                                end module pebbles''',
                             ["Module 'pebbles' is missing an "
                              + "implicit statement"])])
    def containing_program_unit(self, request):
        '''
        Parameter fixture giving permutations of a program unit with or without
        an "explicit none".
        '''
        # pylint: disable=no-self-use
        yield request.param[0], request.param[1]

    @pytest.fixture(scope='class',
                    params=[('', []),
                            ('''subroutine thing()
                                implicit none
                                write(6, '("hoo")')
                                end subroutine thing''', []),
                            ('''subroutine thang()
                                write(6, '("hoo")')
                                end subroutine thang''',
                             ["Subroutine 'thang' is missing an "
                              + "implicit statement"]),
                            ('''function theng()
                                implicit none
                                character(3) :: theng
                                theng = 'hoo'
                                end function theng''', []),
                            ('''function thong()
                                character(3) :: thong
                                thang = 'hoo'
                                end function thong''',
                             ["Function 'thong' is missing an "
                              + "implicit statement"])])
    def subprogram_implicit(self, request):
        '''
        Parameter fixture giving permutations of a procedure with or without an
        "implicit none".
        '''
        # pylint: disable=no-self-use
        yield request.param[0], request.param[1]

    @pytest.fixture(scope='class',
                    params=[('', []),
                            ('''subroutine teapot()
                                implicit none
                                write(6, '("hoo")')
                                end subroutine teapot''', []),
                            ('''subroutine cheese()
                                write(6, '("hoo")')
                                end subroutine cheese''',
                             ["Subroutine 'cheese' is missing "
                              + "an implicit statement"]),
                            ('''function fish()
                                implicit none
                                character(3) :: fish
                                fish = 'hoo'
                                end function fish''', []),
                            ('''function wibble()
                                character(3) :: wibble
                                wibble = 'hoo'
                                end function wibble''',
                             ["Function 'wibble' is missing "
                              + "an implicit statement"])])
    def second_subprogram_implicit(self, request):
        '''
        Parameter fixture giving permutations of a procedure with or without
        an "implicit none".
        '''
        # pylint: disable=no-self-use
        yield request.param[0], request.param[1]

    def test_implicit_double(self, containing_program_unit,
                             subprogram_implicit,
                             second_subprogram_implicit):
        '''
        Checks all the permutations of two contained procedures.
        '''
        # pylint: disable=no-self-use
        procedure = '\n'.join([subprogram_implicit[0],
                               second_subprogram_implicit[0]])
        text = containing_program_unit[0].format(procedure=procedure)
        reader = SourceStringReader(text)
        source = FortranSource(reader)

        expectation = []
        expectation.extend(containing_program_unit[1])
        expectation.extend(subprogram_implicit[1])
        expectation.extend(second_subprogram_implicit[1])

        unit_under_test = stylist.rule.MissingImplicit('none')
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation


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
        #pylint: disable=no-self-use
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
                            [('missing_mod', []),('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']),('missing_mod',[])]])
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
                            [('missing_mod', []),('present_mod', ['stuff'])],
                            [('present_mod', ['stuff']),('missing_mod',[])]])
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
        def prepare( params ):
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
            unit_under_test = stylist.rule.MissingOnly(ignore=ignorance)
        else:
            unit_under_test = stylist.rule.MissingOnly()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
