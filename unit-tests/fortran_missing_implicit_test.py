#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the rule for missing implicit statements.
"""
from typing import List, Tuple

import pytest  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


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
def empty_program_unit_implicit(request: FixtureRequest) \
        -> Tuple[str, List[str]]:
    """
    Parameter fixture giving permutations of program unit with and without
    "implicit none".
    """
    return request.param[0], request.param[1]


@pytest.fixture(scope='module',
                params=[True, False])
def require_always(request: FixtureRequest) -> bool:
    """
    Whether to enable "always require implicit" or not.
    """
    return request.param


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
def containing_program_unit(request: FixtureRequest) -> Tuple[str, List[str]]:
    """
    Parameter fixture giving permutations of a program unit with or without
    an "explicit none".
    """
    return request.param[0], request.param[1]


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
def subprogram_implicit(request: FixtureRequest) -> Tuple[str, List[str]]:
    """
    Parameter fixture giving permutations of a procedure with or without an
    "implicit none".
    """
    return request.param[0], request.param[1]


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
def second_subprogram_implicit(request: FixtureRequest) \
        -> Tuple[str, List[str]]:
    """
    Parameter fixture giving permutations of a procedure with or without
    an "implicit none".
    """
    return request.param[0], request.param[1]


class TestMissingImplicit(object):
    """
    Tests the checker of missing implicit statements.
    """
    def test_implicit(self,
                      empty_program_unit_implicit: Tuple[str, List[str]]) \
            -> None:
        """
        Checks all permutations of program units.
        """
        reader = SourceStringReader(empty_program_unit_implicit[0])
        source = FortranSource(reader)

        expectation = []
        for thing in empty_program_unit_implicit[1]:
            expectation.append(f"1: {thing}")

        unit_under_test = stylist.fortran.MissingImplicit()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation

    def test_implicit_double(
            self,
            containing_program_unit: Tuple[str, List[str]],
            subprogram_implicit: Tuple[str, List[str]],
            second_subprogram_implicit: Tuple[str, List[str]],
            require_always: bool) -> None:
        """
        Checks all the permutations of two contained procedures.
        """
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
        if require_always:
            for thing in subprogram_implicit[1]:
                expectation.append(f"{insert_line}: {thing}")
            for thing in second_subprogram_implicit[1]:
                expectation.append(f"{insert_line + first_len}: {thing}")

        unit_under_test = stylist.fortran.MissingImplicit(
            require_everywhere=require_always)
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
