#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Test of the rule for missing pointer initialisation.
"""
from typing import List

import pytest  # type: ignore

import stylist.fortran
from stylist.source import FortranSource, SourceStringReader


class TestMissingPointerInit(object):
    """
    Tests the checker of missing pointer initialisation.
    """
    @pytest.fixture(scope='class',
                    params=['program', 'module'])
    def prog_unit(self, request):
        """
        Parameter fixture giving program unit types.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=['', 'pointer', 'nullpointer'])
    def type_pointer(self, request):
        """
        Parameter fixture giving pointer type for program unit.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=['', 'pointer', 'nullpointer'])
    def unit_pointer(self, request):
        """
        Parameter fixture giving pointer type for program unit.
        """
        return request.param

    @pytest.fixture(scope='class',
                    params=['', 'pointer', 'nullpointer'])
    def proc_pointer(self, request):
        """
        Parameter fixture giving pointer type for procedure.
        """
        return request.param

    _ATTR_MAP = {'': '',
                 'pointer': ', pointer',
                 'nullpointer': ', pointer'}
    _DECL_MAP = {'': 'normal',
                 'pointer': 'bare',
                 'nullpointer': 'null => null()'}

    def test_pointer_init(self,
                          prog_unit: str,
                          type_pointer: str,
                          unit_pointer: str,
                          proc_pointer: str) -> None:
        """
        Checks that the rule reports missing pointer initialisation correctly.
        """
        template = '''
{prog_unit} test
  implicit none
  private
  type foo_type
    private
    integer{type_attr} :: type_{type_decl}, second_type_{type_decl}
    ! Procedure pointers have to be pointers.
    procedure(some_if), nopass, pointer :: type_proc_pointer_{type_decl}, &
                                           other_type_proc_pointer_{type_decl}
  end type foo_type
  type(foo_type){unit_attr} :: unit_{unit_decl}
  procedure(some_if){unit_attr} :: unit_proc_{unit_decl}
contains
  ! A comment for the function
  !
  function qux() result(answer)
    implicit none
    ! It isn't possible to initialise function return variables
    real, pointer :: answer(:)
  end function qux
  !
  ! Comment for the subroutine
  !
  subroutine bar()
    implicit none
    type(foo_type){proc_attr} :: proc_{proc_decl}
    procedure(some_if){proc_attr} :: proc_proc_{proc_decl}
    integer{proc_attr} :: proc_var_{proc_decl}
  end subroutine bar
  logical function whatev()
    ! Functions may also be declared this way.
    implicit none
    whatev = .true.
  end function whatev
  subroutine baz( thing, thang, thong, bong )
    implicit none
    ! Intent in arguments aren't initialised
    type(foo_type), intent(in), pointer :: thing
    procedure(some_if), intent(in), pointer :: thang
    ! Oddly intent out arguments can't be initialised either
    logical, intent(out), pointer :: bong
    !Intent inout arguments aren't initialised
    real, intent(in out), pointer :: thong(:)
  end subroutine baz
end {prog_unit} test
'''

        expectation: List[str] = []
        message = '{line}: Declaration of pointer ' \
                  '"{name}" without initialisation.'
        if type_pointer != 'nullpointer':
            suffix = self._DECL_MAP[type_pointer].partition(' ')[0]
            expectation.extend([
                message.format(line=9,
                               name=f'other_type_proc_pointer_{suffix}'),
                message.format(line=9,
                               name=f'type_proc_pointer_{suffix}')
            ])
        if type_pointer == 'pointer':
            expectation.extend([message.format(line=7,
                                               name='second_type_bare'),
                                message.format(line=7,
                                               name='type_bare')])
        if proc_pointer == 'pointer':
            expectation.extend([message.format(line=27,
                                               name='proc_bare'),
                                message.format(line=28,
                                               name='proc_proc_bare'),
                                message.format(line=29,
                                               name='proc_var_bare')])
        if unit_pointer == 'pointer':
            expectation.extend([message.format(line=12,
                                               name='unit_bare'),
                                message.format(line=13,
                                               name='unit_proc_bare')])
        expectation.sort(key=lambda x: (int(x.split(':', 1)[0]),
                                        x.split(':', 1)))

        text = template.format(
            prog_unit=prog_unit,
            type_attr=self._ATTR_MAP[type_pointer],
            type_decl=self._DECL_MAP[type_pointer],
            unit_attr=self._ATTR_MAP[unit_pointer],
            unit_decl=self._DECL_MAP[unit_pointer],
            proc_attr=self._ATTR_MAP[proc_pointer],
            proc_decl=self._DECL_MAP[proc_pointer])
        print(text)  # Shows up in failure reports, for debugging
        reader = SourceStringReader(text)
        source = FortranSource(reader)
        unit_under_test = stylist.fortran.MissingPointerInit()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        issue_descriptions.sort(key=lambda x: (int(x.split(':', 1)[0]),
                                               x.split(':', 1)))
        print(issue_descriptions)
        print(expectation)
        assert issue_descriptions == expectation
