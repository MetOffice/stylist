#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Tests of the rule for missing implicit statements.
'''
import fparser  # type: ignore
import pytest  # type: ignore
import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


@pytest.fixture
def simple_source():
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


@pytest.fixture(scope='module',
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
def empty_program_unit_implicit(request):
    '''
    Parameter fixture giving permutations of program unit with and without
    "implicit none".
    '''
    # pylint: disable=no-self-use
    yield request.param[0], request.param[1]


@pytest.fixture(scope='module',
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
def containing_program_unit(request):
    '''
    Parameter fixture giving permutations of a program unit with or without
    an "explicit none".
    '''
    # pylint: disable=no-self-use
    yield request.param[0], request.param[1]


@pytest.fixture(scope='module',
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
def subprogram_implicit(request):
    '''
    Parameter fixture giving permutations of a procedure with or without an
    "implicit none".
    '''
    # pylint: disable=no-self-use
    yield request.param[0], request.param[1]


@pytest.fixture(scope='module',
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
def second_subprogram_implicit(request):
    '''
    Parameter fixture giving permutations of a procedure with or without
    an "implicit none".
    '''
    # pylint: disable=no-self-use
    yield request.param[0], request.param[1]


class TestMissingImplicit(object):
    '''
    Tests the checker of missing implicit statements.
    '''
    def test_implicit(self, empty_program_unit_implicit):
        # pylint: disable=no-self-use
        '''
        Checks all permutations of program units.
        '''
        reader = SourceStringReader(empty_program_unit_implicit[0])
        source = FortranSource(reader)

        expectation = []
        for thing in empty_program_unit_implicit[1]:
            expectation.append(f"1: {thing}")

        unit_under_test = stylist.fortran.MissingImplicit('none')
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation

    def test_implicit_double(self, containing_program_unit,
                             subprogram_implicit,
                             second_subprogram_implicit):
        '''
        Checks all the permutations of two contained procedures.
        '''
        # pylint: disable=no-self-use
        procedure = '\n'.join([subprogram_implicit[0],
                               second_subprogram_implicit[0]]).strip()
        text = containing_program_unit[0].format(procedure=procedure)
        reader = SourceStringReader(text)
        source = FortranSource(reader)

        insert_point = containing_program_unit[0].find('{procedure}')
        insert_line = containing_program_unit[0].count('\n',
                                                       0,
                                                       insert_point) + 1
        first_len = subprogram_implicit[0].count('\n')
        if first_len > 0:
            first_len += 1

        expectation = []
        for thing in containing_program_unit[1]:
            expectation.append(f"1: {thing}")
        for thing in subprogram_implicit[1]:
            expectation.append(f"{insert_line}: {thing}")
        for thing in second_subprogram_implicit[1]:
            expectation.append(f"{insert_line + first_len}: {thing}")

        unit_under_test = stylist.fortran.MissingImplicit('none')
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
