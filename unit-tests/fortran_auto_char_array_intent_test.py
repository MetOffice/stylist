"""
Tests for the auto char array intent rule
"""

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader

TEST_CASE = """
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
        ! A declaration with non-intent attribute, no exception
        character(len=*), parameter :: alt_attr = "sample"
    end subroutine char_input

end program cases
"""

TEST_EXPECTATION = [
    ('12: Arguments of type character(*) must have intent IN, '
        'but autochar_inout has intent INOUT.'),
    ('14: Arguments of type character(*) must have intent IN, '
        'but autochar_out has intent OUT.')
]


class TestAutoCharArrayIntent:
    """
    Tests the rule that variable length character arguments should
    have intent(in)
    """

    def test(self):
        """
        Ensures the test case produces exactly the issues in expectation
        """
        reader = SourceStringReader(TEST_CASE)
        source = FortranSource(reader)
        unit_under_test = stylist.fortran.AutoCharArrayIntent()
        issues = unit_under_test.examine(source)
        strings = [str(issue) for issue in issues]

        assert strings == TEST_EXPECTATION
