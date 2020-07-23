#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the generic rules.
"""
import pytest  # type: ignore

import stylist.rule
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


class TestTrailingWhitespace(object):
    """
    Tests the checker of trailing whitespace.
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
        yield request.param

    def test_examples(self, example_source):
        """
        Ensures trailing whitespace is detected on the correct lines.
        """
        unit_under_test = stylist.rule.TrailingWhitespace()
        reader = SourceStringReader(example_source[0])
        issues = unit_under_test.examine(reader)
        assert (
            [str(issue) for issue in issues]
            == [str(eln) + ': Found trailing white space'
                for eln in example_source[1]]
        )
