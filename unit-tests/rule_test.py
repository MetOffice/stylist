#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the generic rules.
"""
from textwrap import dedent
from typing import List, Tuple

import pytest  # type: ignore

from stylist.rule import TrailingWhitespace, LimitLineLength
from stylist.source import SourceStringReader


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
'''  # noqa: W291, W293

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

end module trailing_whitespace_in_unit_tests'''  # noqa: W291, W293


class TestTrailingWhitespace:
    """
    Tests the checking of trailing whitespace.
    """
    @pytest.fixture(scope='class',
                    params=[(_NO_TWS, []),
                            (_SOME_TWS, [6, 9]),
                            (_PF_TWS, [5, 21])])
    def example_source(self, request):
        """
        Parameter fixture giving Fortran source with various
        trailing whitespace issues.
        """
        return request.param

    def test_examples(self, example_source: Tuple[str, List[int]]) -> None:
        """
        Ensures trailing whitespace is detected on the correct lines.
        """
        unit_under_test = TrailingWhitespace()
        reader = SourceStringReader(example_source[0])
        issues = unit_under_test.examine(reader)
        assert (
            [str(issue) for issue in issues]
            == [str(eln) + ': Found trailing white space'
                for eln in example_source[1]]
        )


class TestLineLength:
    """
    Tests the line length rule.
    """
    @pytest.fixture(scope='class')
    def source(self) -> SourceStringReader:
        return SourceStringReader(dedent("""
module test_mod

  use module_with_long_name, only : entity_with_long_name

  implicit none

    subroutine procedure_with_long_name
      implicit none
      write(6,'(A)') "This line just fits into 79 characters if you ignore indenting"
      write(6,'(A)') "This line is longer than 79 characters even without the indentation. In fact it is over 120 with indent"
    end subroutine procedure_with_long_name

end module test_mod
        """).strip())  # noqa: E501

    @pytest.fixture(
        scope='class',
        params=[(None, None,
                 ['9: Line exceeds 79 characters',
                  '10: Line exceeds 79 characters']),
                (None, True,
                 ['10: Line exceeds 79 characters after leading whitespace']),
                (40, None,
                 ['3: Line exceeds 40 characters',
                  '9: Line exceeds 40 characters',
                  '10: Line exceeds 40 characters',
                  '11: Line exceeds 40 characters']),
                (40, True,
                 ['3: Line exceeds 40 characters after leading whitespace',
                  '9: Line exceeds 40 characters after leading whitespace',
                  '10: Line exceeds 40 characters after leading whitespace']),
                (120, None,
                 ['10: Line exceeds 120 characters']),
                (120, True,
                 [])])
    def case(self, request):
        return request.param

    def test_case(self, source: SourceStringReader, case) -> None:
        """
        Ensures the default operation is as expected.
        """
        if case[0] is not None and case[1] is not None:
            test_unit = LimitLineLength(length=case[0],
                                        ignore_leading_whitespace=case[1])
        elif case[0] is not None:
            test_unit = LimitLineLength(length=case[0])
        elif case[1] is not None:
            test_unit = LimitLineLength(ignore_leading_whitespace=case[1])
        else:
            test_unit = LimitLineLength()

        issues = test_unit.examine(source)
        assert [str(issue) for issue in issues] \
               == case[2]
