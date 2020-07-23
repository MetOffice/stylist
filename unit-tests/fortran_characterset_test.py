#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tests of the Fortran character set rule.
"""
import pytest  # type: ignore
import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


_SIMPLE_NO_PROBLEMS = '''
                      program immaculate

                        use iso_fortran_env, only : output_unit

                        implicit none

                        ! There are no character set errors here

                        write( output_unit, '("Cheese and ", A)' ) "Beef"

                      end program immaculate
                      '''
_SIMPLE_TAB = '''
              program tab_mistake

                implicit none

                write(6, '(A)')	'Hello'

              end program tab_mistake
              '''
_SIMPLE_COMMENT = '''
                  program exotic_comment

                    implicit none

                    ! Comments may have	exotics

                  end program exotic_comment
                  '''
_SIMPLE_STRINGS = '''
                  program exotic_strings

                    implicit none

                    write(6, '(A)') 'First	string'
                    write(6,'(A)') "Second	string"

                  end program exotic_strings
                  '''
_SIMPLE_FORMAT = '''
                 program exotic_format

                   implicit none

                   write(6,'("This	thing: ", I0)') 4

                 end program exotic_format
                 '''


@pytest.fixture(scope='module',
                params=[(_SIMPLE_NO_PROBLEMS, []),
                        (_SIMPLE_TAB,
                         ["6: Found character '\\t' not in "
                          + "Fortran character set"]),
                        (_SIMPLE_COMMENT, []),
                        (_SIMPLE_STRINGS, []),
                        (_SIMPLE_FORMAT, [])])
def simple_source(request):
    """
    Parameter fixture giving a simple Fortran source with various
    caracterset issues.
    """
    yield request.param


class TestFortranCharacterset(object):
    """
    Tests the rule which ensures none Fortran characters do not appear in the
    source.
    """
    def test_simple(self, simple_source):
        """
        Ensures a given input source generates the correct issue list.
        """
        unit_under_test = stylist.fortran.FortranCharacterset()
        reader = SourceStringReader(simple_source[0])
        source = FortranSource(reader)
        issues = unit_under_test.examine(source)
        assert [str(issue) for issue in issues] == simple_source[1]
