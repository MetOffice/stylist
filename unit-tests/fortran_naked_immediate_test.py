#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the rule for immediate values with precision.
"""
from textwrap import dedent

from stylist.fortran import NakedImmediate
from stylist.source import FortranSource, SourceStringReader


class TestNakedImmediate:
    """
    Tests the rule for immediate values without precision.
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

        test_unit = NakedImmediate()
        issues = test_unit.examine(source)

        assert [str(issue) for issue in issues] == []

    def test_bad(self):
        text = dedent('''
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

        reader = SourceStringReader(text)
        source = FortranSource(reader)

        test_unit = NakedImmediate()
        issues = test_unit.examine(source)

        # Due to an issue with fparser and continuation lines the line numbers
        # are for the first line of the continuation block in which the error
        # is found.
        #
        # Disabling pycodestyle for lines longer than 80 characters is messy
        # but breaking up the lines would be worse.
        #
        assert sorted([str(issue) for issue in issues]) == [
            '11: Immediate value assigned to "larger_init_float_mod" without kind',  # noqa
            '14: Immediate value assigned to "smaller_init_int_type" without kind',  # noqa
            '16: Immediate value assigned to "smaller_init_float_type" without kind',  # noqa
            '18: Immediate value assigned to "larger_init_int_type" without kind',  # noqa
            '20: Immediate value assigned to "larger_init_float_type" without kind',  # noqa
            '26: Immediate value assigned to "smaller_init_int_sub" without kind',  # noqa
            '28: Immediate value assigned to "smaller_init_float_sub" without kind',  # noqa
            '30: Immediate value assigned to "larger_init_int_sub" without kind',  # noqa
            '32: Immediate value assigned to "larger_init_float_sub" without kind',  # noqa
            '34: Immediate value assigned to "smaller_int_mod" without kind',
            '35: Immediate value assigned to "smaller_init_int_mod" without kind',  # noqa
            '36: Immediate value assigned to "smaller_float_mod" without kind',
            '37: Immediate value assigned to "smaller_init_float_mod" without kind',  # noqa
            '38: Immediate value assigned to "larger_int_mod" without kind',
            '39: Immediate value assigned to "larger_init_int_mod" without kind',  # noqa
            '40: Immediate value assigned to "larger_float_mod" without kind',
            '41: Immediate value assigned to "larger_init_float_mod" without kind',  # noqa
            '42: Immediate value assigned to "smaller_int_sub" without kind',
            '43: Immediate value assigned to "smaller_init_int_sub" without kind',  # noqa
            '44: Immediate value assigned to "smaller_float_sub" without kind',
            '45: Immediate value assigned to "smaller_init_float_sub" without kind',  # noqa
            '46: Immediate value assigned to "larger_int_sub" without kind',
            '47: Immediate value assigned to "larger_init_int_sub" without kind',  # noqa
            '48: Immediate value assigned to "larger_float_sub" without kind',
            '49: Immediate value assigned to "larger_init_float_sub" without kind',  # noqa
            '56: Immediate value assigned to "smaller_init_int_prog" without kind',  # noqa
            '58: Immediate value assigned to "smaller_init_float_prog" without kind',  # noqa
            '5: Immediate value assigned to "smaller_init_int_mod" without kind',  # noqa
            '60: Immediate value assigned to "larger_init_int_prog" without kind',  # noqa
            '62: Immediate value assigned to "larger_init_float_prog" without kind',  # noqa
            '64: Immediate value assigned to "smaller_int_prog" without kind',
            '65: Immediate value assigned to "smaller_init_int_prog" without kind',  # noqa
            '66: Immediate value assigned to "smaller_float_prog" without kind',  # noqa
            '67: Immediate value assigned to "smaller_init_float_prog" without kind',  # noqa
            '68: Immediate value assigned to "larger_int_prog" without kind',
            '69: Immediate value assigned to "larger_init_int_prog" without kind',  # noqa
            '70: Immediate value assigned to "larger_float_prog" without kind',
            '71: Immediate value assigned to "larger_init_float_prog" without kind',  # noqa,
            '7: Immediate value assigned to "smaller_init_float_mod" without kind',  # noqa
            '9: Immediate value assigned to "larger_init_int_mod" without kind'
        ]
