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
from stylist.source import (FortranPreProcessor,
                            FortranSource,
                            SourceStringReader)


class TestKindPattern:
    """
    Test the checking of kind patterns.
    """
    def test_correct_variables(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer(bully_beef), parameter :: global_param_int
          integer(kind=bully_beef), parameter :: named_global_param_int
          real(sheep_cheese), parameter :: global_param_real
          real(kind=sheep_cheese), parameter :: named_global_param_real
          integer(medium_beef) :: global_int
          integer(kind=medium_beef) :: named_global_int
          integer(salt_beef) :: global_first, global_second
          integer(kind=salt_beef) :: named_global_first, named_global_second
          real(soft_cheese) :: global_float
          real(kind=soft_cheese) :: named_global_float
          logical(who_cares) :: global_bool
          logical(kind=who_cares) :: named_global_bool
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(integer=r'.+_beef',
                                      real=re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)
        assert len(issues) == 0

    def test_correct_variables_preprocessed(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer(kind=medium_beef) :: named_global_int
          integer(medium_beef) :: global_int
          integer(kind=salt_beef) :: named_global_first, named_global_second
          integer(salt_beef) :: global_first, global_second
          real(kind=soft_cheese) :: named_global_float
          real(soft_cheese) :: global_float
          logical(kind=who_cares) :: named_global_bool
          logical(who_cares) :: global_bool
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        preproc = FortranPreProcessor(reader)
        source = FortranSource(preproc)
        unit_under_test = KindPattern(integer=r'.+_beef',
                                      real=re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)
        assert len(issues) == 0

    def test_correct_procedures(self):
        case = dedent("""
        module passing_mod
        contains
          function thing(arg_int, &
                         named_arg_int, &
                         arg_float, &
                         named_arg_float, &
                         arg_float_1, &
                         named_arg_float_1, &
                         arg_float_2, &
                         named_arg_float_2, &
                         arg_bool, &
                         named_arg_bool) result(return_int)
            implicit none
            integer(rare_beef), intent(in) :: arg_int
            integer(kind=rare_beef), intent(in) :: named_arg_int
            real(hard_cheese), intent(out) :: arg_float
            real(kind=hard_cheese), intent(out) :: named_arg_float
            real(stinky_cheese), intent(in) :: arg_float_1, arg_float_2
            real(kind=stinky_cheese), intent(in) :: named_arg_float_1, &
                                                    named_arg_float_2
            logical(no_one_cares), intent(inout) :: arg_bool
            logical(kind=no_one_cares), intent(inout) :: named_arg_bool
            integer(well_done_beef) :: return_int
          end function thing
          subroutine other_thing(arg_int, named_arg_int)
            integer(bare_beef), intent(in) :: arg_int
            integer(kind=bare_beef), intent(in) :: named_arg_int
            implicit none
          end subroutine other_thing
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(integer=r'.+_beef',
                                      real=re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)
        assert len(issues) == 0

    def test_correct_methods(self):
        case = dedent("""
        module passing_mod
          implicit none
          type some_type
            integer(bloody_beef) :: member_int
            integer(kind=bloody_beef) :: named_member_int
            integer(marbled_beef) :: member_int_1, member_int_2
            integer(kind=marbled_beef) :: nmd_member_int_1, nmd_member_int_2
            real(blue_cheese) :: member_float
            real(kind=blue_cheese) :: named_member_float
            real(green_cheese) :: member_float_1, member_float_2
            real(kind=green_cheese) :: nmd_member_float_1, nmd_member_float_2
            logical(no_difference) :: member_bool
            logical(kind=no_difference) :: named_member_bool
          contains
            procedure method
            procedure other_method
          end type some_type
        contains
          function method(this, &
                          marg_int, &
                          named_marg_int, &
                          marg_int_1, &
                          named_marg_int_1, &
                          marg_int_2, &
                          named_marg_int_2, &
                          marg_float, &
                          named_marg_float, &
                          marg_bool, &
                          named_marg_bool) result(named_return_float)
            implicit none
            class(some_type), intent(in) :: this
            integer(cremated_beef), intent(in) :: marg_int
            integer(kind=cremated_beef), intent(in) :: named_marg_int
            integer(shredded_beef), intent(out) :: marg_int_1, marg_int_2
            integer(kind=shredded_beef), intent(out) :: named_marg_int_1, &
                                                        named_marg_int_2
            real(sheep_cheese), intent(out) :: marg_float
            real(kind=sheep_cheese), intent(out) :: named_marg_float
            logical(sigh), intent(inout) :: marg_bool
            logical(kind=sigh), intent(inout) :: named_marg_bool
            real(kind=goat_cheese) :: named_return_float
          end function method
          subroutine other_method(this, &
                                  marg_int, &
                                  named_marg_int)
            class(some_type), intent(in) :: this
            integer(incinerated_beef), intent(in) :: marg_int
            integer(kind=incinerated_beef), intent(in) :: named_marg_int
          end subroutine other_method
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(integer=r'.+_beef',
                                      real=re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)
        assert [str(issue) for issue in issues] == []

    def test_failing(self):
        case = dedent("""
        module passing_mod
          implicit none
          integer(soft_cheese) :: global_int
          integer(kind=soft_cheese) :: named_global_int
          integer(blue_cheese) :: global_first, global_second
          integer(kind=blue_cheese) :: named_global_first, named_global_second
          real(medium_beef) :: global_float
          real(kind=medium_beef) :: named_global_float
          logical(who_cares) :: global_bool
          logical(kind=who_cares) :: global_bool
          type some_type
            integer(green_cheese) :: member_int
            integer(kind=green_cheese) :: named_member_int
            integer(goat_cheese) :: member_int_1, member_int_2
            integer(kind=goat_cheese) :: named_member_int_1, named_member_int_2
            real(salt_beef) :: member_float
            real(kind=salt_beef) :: named_member_float
            real(bloody_beef) :: member_float_1, member_float_2
            real(kind=bloody_beef) :: named_member_float_1, &
                                      named_member_float_2
            logical(no_difference) :: member_bool
            logical(kind=no_difference) :: named_member_bool
          contains
            procedure method
          end type some_type
        contains
          function thing(arg_int, arg_float, arg_bool) result(return_int)
            implicit none
            integer(hard_cheese), intent(in) :: arg_int
            integer(kind=hard_cheese), intent(in) :: named_arg_int
            real(rare_beef), intent(out) :: arg_float
            real(kind=rare_beef), intent(out) :: named_arg_float
            real(marbled_beef), intent(in) :: arg_float_1, arg_float_2
            real(kind=marbled_beef), intent(in) :: named_arg_float_1, &
                                                   named_arg_float_2
            logical(no_one_cares), intent(inout) :: arg_bool
            logical(kind=no_one_cares), intent(inout) :: named_arg_bool
            integer(stinky_cheese) :: return_int
          end function thing
          function method(this, &
                          marg_int, &
                          marg_float, &
                          marg_bool) result(named_return_float)
            implicit none
            integer(sheep_cheese), intent(in) :: marg_int
            integer(kind=sheep_cheese), intent(in) :: named_marg_int
            integer(chewy_cheese), intent(out) :: marg_int_1, marg_int_2
            integer(kind=chewy_cheese), intent(out) :: named_marg_int_1, &
                                                       named_marg_int_2
            real(shredded_beef), intent(out) :: marg_float
            real(kind=shredded_beef), intent(out) :: named_marg_float
            logical(sigh), intent(inout) :: marg_bool
            logical(kind=sigh), intent(inout) :: named_marg_bool
            real(kind=cremated_beef) :: named_return_float
          end function method
        end module passing_mod
        """)

        reader = SourceStringReader(case)
        source = FortranSource(reader)
        unit_under_test = KindPattern(integer=re.compile(r'.+_beef'),
                                      real=r'.+_cheese')
        issues = unit_under_test.examine(source)

        assert len(issues) == 28

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
          function method(this, &
                          marg_int, &
                          marg_float, &
                          marg_bool) result(return_float)
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
        unit_under_test = KindPattern(integer=r'.+_beef',
                                      real=re.compile(r'.+_cheese'))
        issues = unit_under_test.examine(source)
        assert len(issues) == 0
