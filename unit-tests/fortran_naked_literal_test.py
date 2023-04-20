#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the rule for literal values with precision.
"""
from textwrap import dedent

from stylist.fortran import NakedLiteral
from stylist.source import FortranSource, SourceStringReader


class TestNakedLiteral:
    """
    Tests the rule for literal values without precision.
    """
    def test_good(self):
        text = dedent('''
                      module good_mod
                        use iso_fortran_env, only : int64, int32, &
                                                    real64, real32
                        implicit none
                        integer(int32) :: smaller_int_mod, &
                                          smaller_init_int_mod = 4_int32
                        real(real32) :: smaller_float_mod, &
                                        smaller_init_float_mod = 3.141_real32
                        integer(int64) :: larger_int_mod, &
                                          larger_init_int_mod = 40_int64
                        real(real64) :: larger_float_mod, &
                                        larger_init_float_mod = 31.41_real64
                        type test_type
                          integer(int32) :: smaller_int_type, &
                                            smaller_init_int_type = 5_int32
                          real(real32) :: smaller_float_type, &
                                          smaller_init_float_type = 4.0_real32
                          integer(int64) :: larger_int_type, &
                                            larger_init_int_type = 50_int64
                          real(real64) :: larger_float_type, &
                                          larger_init_float_type = 40.0_real64
                        end type test_type
                      contains
                        subroutine something()
                          implicit none
                          integer(int32) :: small_int_sub, &
                                            smaller_init_int_sub = 7_int32
                          real(real32) :: smaller_float_sub, &
                                          smaller_init_float_sub = 6.7_real32
                          integer(int64) :: larger_int_sub, &
                                            larger_init_int_sub = 70_int64
                          real(real64) :: larger_float_sub, &
                                          larger_init_float_sub = 67.0_real64
                          smaller_int_mod = 1_int32
                          smaller_init_int_mod = 2_int32
                          smaller_float_mod = 3.0_real32
                          smaller_init_float_mod = 4.0_real32
                          larger_int_mod = 5_int64
                          larger_init_int_mod = 6_int64
                          larger_float_mod = 7.0_real64
                          larger_init_float_mod = 8.0_real64
                          smaller_int_sub = 9_int32
                          smaller_init_int_sub = 10_int32
                          smaller_float_sub = 11.0_real32
                          smaller_init_float_sub = 12.0_real32
                          larger_int_sub = 13_int64
                          larger_init_int_sub = 14_int64
                          larger_float_sub = 15.0_real64
                          larger_init_float_sub = 16.0_real64
                        end subroutine something
                      end module good_mod
                      program good
                        use iso_fortran_env, only : int64, int32, &
                                                    real64, real32
                        implicit none
                        integer(int32) :: smaller_int_prog, &
                                          smaller_init_int_prog = 11_int32
                        real(real32) :: smaller_float_prog, &
                                        smaller_init_float_prog = 8.2_real32
                        integer(int64) :: larger_int_prog, &
                                          larger_init_int_prog = 110_int64
                        real(real64) :: larger_float_prog, &
                                        larger_init_float_prog = 82.0_real64
                        smaller_int_prog = 2_int32
                        smaller_init_int_prog = 3_int32
                        smaller_float_prog = 4.9_real32
                        smaller_init_float_prog = 5.2_real32
                        larger_int_prog = 6_int64
                        larger_init_int_prog = 7_int64
                        larger_float_prog = 8.1_real64
                        larger_init_float_prog = 9.2_real64
                      end program good
                      ''').strip()

        reader = SourceStringReader(text)
        source = FortranSource(reader)

        test_unit = NakedLiteral()
        issues = test_unit.examine(source)

        assert [str(issue) for issue in issues] == []

    _bad_text = dedent('''
                  module good_mod
                    use iso_fortran_env, only : int64, int32, &
                                                real64, real32
                    implicit none
                    integer(int32) :: smaller_int_mod, &
                                      smaller_init_int_mod = 4
                    real(real32) :: smaller_float_mod, &
                                    smaller_init_float_mod = 3.141
                    integer(int64) :: larger_int_mod, &
                                      larger_init_int_mod = 40
                    real(real64) :: larger_float_mod, &
                                    larger_init_float_mod = 31.41
                    type test_type
                      integer(int32) :: smaller_int_type, &
                                        smaller_init_int_type = 5
                      real(real32) :: smaller_float_type, &
                                      smaller_init_float_type = 4.0
                      integer(int64) :: larger_int_type, &
                                        larger_init_int_type = 50
                      real(real64) :: larger_float_type, &
                                      larger_init_float_type = 40.0
                    end type test_type
                  contains
                    subroutine something()
                      implicit none
                      integer(int32) :: small_int_sub, &
                                        smaller_init_int_sub = 7
                      real(real32) :: smaller_float_sub, &
                                      smaller_init_float_sub = 6.7
                      integer(int64) :: larger_int_sub, &
                                        larger_init_int_sub = 70
                      real(real64) :: larger_float_sub, &
                                      larger_init_float_sub = 67.0
                      smaller_int_mod = 1
                      smaller_init_int_mod = 2
                      smaller_float_mod = 3.0
                      smaller_init_float_mod = 4.0
                      larger_int_mod = 5
                      larger_init_int_mod = 6
                      larger_float_mod = 7.0
                      larger_init_float_mod = 8.0
                      smaller_int_sub = 9
                      smaller_init_int_sub = 10
                      smaller_float_sub = 11.0
                      smaller_init_float_sub = 12.0
                      larger_int_sub = 13
                      larger_init_int_sub = 14
                      larger_float_sub = 15.0
                      larger_init_float_sub = 16.0
                    end subroutine something
                  end module good_mod
                  program good
                    use iso_fortran_env, only : int64, int32, &
                                                real64, real32
                    implicit none
                    integer(int32) :: smaller_int_prog, &
                                      smaller_init_int_prog = 11
                    real(real32) :: smaller_float_prog, &
                                    smaller_init_float_prog = 8.2
                    integer(int64) :: larger_int_prog, &
                                      larger_init_int_prog = 110
                    real(real64) :: larger_float_prog, &
                                    larger_init_float_prog = 82.0
                    smaller_int_prog = 2
                    smaller_init_int_prog = 3
                    smaller_float_prog = 4.9
                    smaller_init_float_prog = 5.2
                    larger_int_prog = 6
                    larger_init_int_prog = 7
                    larger_float_prog = 8.1
                    larger_init_float_prog = 9.2
                  end program good
                  ''').strip()

    # Due to an issue with fparser and continuation lines the line numbers
    # are for the first line of the continuation block in which the error
    # is found.
    #
    _expected_int = [
        '14: Literal value assigned to "smaller_init_int_type" without kind',
        '18: Literal value assigned to "larger_init_int_type" without kind',
        '26: Literal value assigned to "smaller_init_int_sub" without kind',
        '30: Literal value assigned to "larger_init_int_sub" without kind',
        '34: Literal value assigned to "smaller_int_mod" without kind',
        '35: Literal value assigned to "smaller_init_int_mod" without kind',
        '38: Literal value assigned to "larger_int_mod" without kind',
        '39: Literal value assigned to "larger_init_int_mod" without kind',
        '42: Literal value assigned to "smaller_int_sub" without kind',
        '43: Literal value assigned to "smaller_init_int_sub" without kind',
        '46: Literal value assigned to "larger_int_sub" without kind',
        '47: Literal value assigned to "larger_init_int_sub" without kind',
        '56: Literal value assigned to "smaller_init_int_prog" without kind',
        '5: Literal value assigned to "smaller_init_int_mod" without kind',
        '60: Literal value assigned to "larger_init_int_prog" without kind',
        '64: Literal value assigned to "smaller_int_prog" without kind',
        '65: Literal value assigned to "smaller_init_int_prog" without kind',
        '68: Literal value assigned to "larger_int_prog" without kind',
        '69: Literal value assigned to "larger_init_int_prog" without kind',
        '9: Literal value assigned to "larger_init_int_mod" without kind'
    ]

    # Due to an issue with fparser and continuation lines the line numbers
    # are for the first line of the continuation block in which the error
    # is found.
    #
    # Disabling pycodestyle for lines longer than 80 characters is messy
    # but breaking up the lines would be worse.
    #
    _expected_float = [
        '11: Literal value assigned to "larger_init_float_mod" without kind',
        '16: Literal value assigned to "smaller_init_float_type" without kind',  # noqa
        '20: Literal value assigned to "larger_init_float_type" without kind',  # noqa
        '28: Literal value assigned to "smaller_init_float_sub" without kind',  # noqa
        '32: Literal value assigned to "larger_init_float_sub" without kind',
        '36: Literal value assigned to "smaller_float_mod" without kind',
        '37: Literal value assigned to "smaller_init_float_mod" without kind',  # noqa
        '40: Literal value assigned to "larger_float_mod" without kind',
        '41: Literal value assigned to "larger_init_float_mod" without kind',
        '44: Literal value assigned to "smaller_float_sub" without kind',
        '45: Literal value assigned to "smaller_init_float_sub" without kind',  # noqa
        '48: Literal value assigned to "larger_float_sub" without kind',
        '49: Literal value assigned to "larger_init_float_sub" without kind',
        '58: Literal value assigned to "smaller_init_float_prog" without kind',  # noqa
        '62: Literal value assigned to "larger_init_float_prog" without kind',  # noqa
        '66: Literal value assigned to "smaller_float_prog" without kind',
        '67: Literal value assigned to "smaller_init_float_prog" without kind',  # noqa
        '70: Literal value assigned to "larger_float_prog" without kind',
        '71: Literal value assigned to "larger_init_float_prog" without kind',  # noqa,
        '7: Literal value assigned to "smaller_init_float_mod" without kind',
    ]

    def test_both(self):
        reader = SourceStringReader(self._bad_text)
        source = FortranSource(reader)

        test_unit = NakedLiteral()
        issues = test_unit.examine(source)

        expected = list(self._expected_int)
        expected.extend(self._expected_float)
        assert sorted([str(issue) for issue in issues]) == sorted(expected)

    def test_integer(self):
        reader = SourceStringReader(self._bad_text)
        source = FortranSource(reader)

        test_unit = NakedLiteral(reals=False)
        issues = test_unit.examine(source)
        assert sorted([str(issue) for issue in issues]) == self._expected_int

    def test_float(self):
        reader = SourceStringReader(self._bad_text)
        source = FortranSource(reader)

        test_unit = NakedLiteral(integers=False)
        issues = test_unit.examine(source)
        assert sorted([str(issue) for issue in issues]) == self._expected_float
