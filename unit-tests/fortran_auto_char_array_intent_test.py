"""
Tests for the auto char array intent rule
"""

from unittest import expectedFailure
import pytest
from _pytest.fixtures import FixtureRequest
from typing import List, Tuple

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader

#TODO More complex variable declarations

test_case = \
"""
program cases
    ! A char array outside a function or subroutine, no exception
    character (*) :: autochar_glob

    contains

    subroutine char_input(autochar_in, autochar_inout, autochar_out, fixedchar)
        ! A char array with proper intent, no exception
        character(*), intent(in)       :: autochar_in
        ! A char array with disallowed intent, exception
        character(*), intent(inout)    :: autochar_inout
        ! A char array with disallowed intent, exception
        character(len=*), intent(out)  :: autochar_out
        ! A char array not passed as a parameter, no exception
        character(*)                   :: autochar_var
        ! A char array with fixed length, no exception
        character(len=10), intent(out) :: fixedchar
    end subroutine char_input

end program cases
"""

class TestAutoCharArrayIntent:
    def test(self):
        reader = SourceStringReader(test_case)
        source = FortranSource(reader)
        unit_under_test = stylist.fortran.AutoCharArrayIntent()
        issues = unit_under_test.examine(source)
        strings = [str(issue) for issue in issues]

        expectation = [
            '12: Arguments of type character(*) must have intent IN, but autochar_inout has intent INOUT.',
            '14: Arguments of type character(*) must have intent IN, but autochar_out has intent OUT.'
        ]

        assert strings == expectation