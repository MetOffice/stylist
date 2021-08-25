##############################################################################
# (c) Crown copyright 2021 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Test of the rule for kind name pattern.
"""
import re
from textwrap import dedent

from stylist.fortran import KindPattern
from stylist.source import FortranSource, SourceStringReader


class TestKindPattern:
    """
    Test the checker of kind patterns.
    """
    def test_passing(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer(medium_beef) :: global_int
          integer(salt_beef) :: global_first, global_second
          real(soft_cheese) :: global_float
          logical(who_cares) :: global_bool
          type some_type
            integer(bloody_beef) :: member_int
            integer(marbled_beef) :: member_int_1, member_int_2
            real(blue_cheese) :: member_float
            real(green_cheese) :: member_float_1, member_float_2
            logical(no_difference) :: member_bool
          contains
            procedure method
          end type some_type
        contains
          function thing(arg_int, arg_float, arg_float_1, arg_float_2, arg_bool) result(return_int)
            implicit none
            integer(rare_beef), intent(in) :: arg_int
            real(hard_cheese), intent(out) :: arg_float
            real(stinky_cheese), intent(in) :: arg_float_1, arg_float_2
            logical(no_one_cares), intent(inout) :: arg_bool
            integer(well_done_beef) :: return_int
          end function thing
          function method(this, marg_int, marg_int_1, marg_int_2, marg_float, marg_bool) result(return_float)
            implicit none
            integer(cremated_beef), intent(in) :: marg_int
            integer(shredded_beef), intent(out) :: marg_int_1, marg_int_2
            real(sheep_cheese), intent(out) :: marg_float
            logical(sigh), intent(inout) :: marg_bool
            real(goat_cheese) :: return_float
          end function method
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(r'.+_beef', re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)

        assert len(issues) == 0

    def test_failing(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer(soft_cheese) :: global_int
          integer(blue_cheese) :: global_first, global_second
          real(medium_beef) :: global_float
          logical(who_cares) :: global_bool
          type some_type
            integer(green_cheese) :: member_int
            integer(goat_cheese) :: member_int_1, member_int_2
            real(salt_beef) :: member_float
            real(bloody_beef) :: member_float_1, member_float_2
            logical(no_difference) :: member_bool
          contains
            procedure method
          end type some_type
        contains
          function thing(arg_int, arg_float, arg_bool) result(return_int)
            implicit none
            integer(hard_cheese), intent(in) :: arg_int
            real(rare_beef), intent(out) :: arg_float
            real(marbled_beef), intent(in) :: arg_float_1, arg_float_2
            logical(no_one_cares), intent(inout) :: arg_bool
            integer(stinky_cheese) :: return_int
          end function thing
          function method(this, marg_int, marg_float, marg_bool) result(return_float)
            implicit none
            integer(sheep_cheese), intent(in) :: marg_int
            integer(chewy_cheese), intent(out) :: marg_int_1, marg_int_2
            real(shredded_beef), intent(out) :: marg_float
            logical(sigh), intent(inout) :: marg_bool
            real(cremated_beef) :: return_float
          end function method
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(r'.+_beef', re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)

        assert len(issues) == 15

    def test_missing_kind(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer :: global_int
          real :: global_float
          logical :: global_bool
          type some_type
            integer :: member_int
            real :: member_float
            logical :: member_bool
          contains
            procedure method
          end type some_type
        contains
          function thing(arg_int, arg_float, arg_bool) result(return_int)
            implicit none
            integer, intent(in) :: arg_int
            real, intent(out) :: arg_float
            logical, intent(inout) :: arg_bool
            integer :: return_int
          end function thing
          function method(this, marg_int, marg_float, marg_bool) result(return_float)
            implicit none
            integer, intent(in) :: marg_int
            real, intent(out) :: marg_float
            logical, intent(inout) :: marg_bool
            real :: return_float
          end function method
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(r'.+_beef', re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)

        assert len(issues) == 0
