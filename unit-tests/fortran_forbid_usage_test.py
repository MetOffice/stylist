#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Test of the rule for missing exit labels.
"""
from textwrap import dedent

from stylist.fortran import ForbidUsage
from stylist.source import FortranSource, SourceStringReader


# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.


class TestForbidUsage(object):
    """
    Tests the rule which forbids usage of certain modules.
    """
    def test_forbid_usage(self) -> None:
        """
        Checks that usage is forbidden.
        """
        source_text = dedent('''
                             module some_mod
                               use fish_mod, only: breem
                               use beef_mod
                               use alpha_mod, only: tiptop
                             contains
                               subroutine stuff()
                                 use grief_mod, only: agro
                                 use alpha_mod
                                 use bingo_mod
                               end subroutine stuff
                             end module some_mod
                             ''').strip()
        reader = SourceStringReader(source_text)
        source = FortranSource(reader)

        test_unit = ForbidUsage('alpha_mod')
        issues = test_unit.examine(source)

        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == [
            "4: Attempt to use forbidden module 'alpha_mod'",
            "8: Attempt to use forbidden module 'alpha_mod'"
        ]

    def test_except_usage(self) -> None:
        """
        Check that exceptions work.
        """
        source_text = dedent('''
                             module teapot_mod
                               use fish_mod, only: breem
                               use beef_mod
                               use ceramic_mod, only: tiptop
                             contains
                               subroutine stuff()
                                 use grief_mod, only: agro
                                 use ceramic_mod
                                 use bingo_mod
                               end subroutine stuff
                             end module teapot_mod
                             module plate_mod
                               use ceramtic_mod
                             contains
                               subroutine nonsense()
                                 use ceramic_mod, only: toptip
                               end subroutine nonsense
                             end module plate_mod
                             module fork_mod
                               use ceramic_mod, only: specialist
                             contains
                               subroutine piffle()
                                 use ceramic_mod
                               end subroutine piffle
                             end module fork_mod
                             ''').strip()
        reader = SourceStringReader(source_text)
        source = FortranSource(reader)

        test_unit = ForbidUsage('ceramic_mod', ['teapot_mod', 'plate_mod'])
        issues = test_unit.examine(source)

        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == [
            "20: Attempt to use forbidden module 'ceramic_mod'",
            "23: Attempt to use forbidden module 'ceramic_mod'"
        ]

    def test_motivating_example(self) -> None:
        mpi_mod_text = dedent('''
                              module mpi_mod
                                use mpi
                              contains
                                subroutine init()
                                  use mpi
                                end subroutine
                              end module mpi_mod
                              ''').strip()

        other_mod_text = dedent('''
                                module other_mod
                                  use  mpi
                                contains
                                  subroutine something()
                                    use mpi
                                  end subroutine
                                end module
                                ''').strip()

        mpi_mod_reader = SourceStringReader(mpi_mod_text)
        mpi_mod_source = FortranSource(mpi_mod_reader)

        other_mod_reader = SourceStringReader(other_mod_text)
        other_mod_source = FortranSource(other_mod_reader)

        test_unit = ForbidUsage('mpi', ['mpi_mod'])
        issues = test_unit.examine(mpi_mod_source)

        assert len(issues) == 0

        issues = test_unit.examine(other_mod_source)

        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == [
            "2: Attempt to use forbidden module 'mpi'",
            "5: Attempt to use forbidden module 'mpi'"
        ]