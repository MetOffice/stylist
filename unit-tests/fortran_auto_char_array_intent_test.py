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

test_case = \
"""
!-----------------------------------------------------------------------------
! (C) Crown copyright 2021 Met Office. All rights reserved.
! The file LICENCE, distributed with this code, contains details of the terms
! under which the code may be used.
!-----------------------------------------------------------------------------
!> Wrap the XIOS context in an object for easier management and cleaner coding.
!>
module lfric_xios_context_mod

  use clock_mod,            only : clock_type
  use io_context_mod,       only : io_context_type, &
                                   io_context_initialiser_type
  use step_calendar_mod,    only : step_calendar_type
  use constants_mod,        only : i_native, &
                                   r_second, &
                                   l_def
  use lfric_xios_clock_mod, only : lfric_xios_clock_type
  use log_mod,              only : log_event,       &
                                   log_level_error, &
                                   log_level_info
  use lfric_xios_file_mod,  only : xios_file_type
  use xios,                 only : xios_close_context_definition, &
                                   xios_context,                  &
                                   xios_context_finalize,         &
                                   xios_context_initialize,       &
                                   xios_get_handle,               &
                                   xios_set_current_context

  implicit none

  public :: filelist_populator
  private

  !> Manages interactions with XIOS.
  !>
  type, public, extends(io_context_type) :: lfric_xios_context_type
    private
    character(:),                 allocatable :: id
    type(xios_context)                        :: handle
    class(lfric_xios_clock_type), allocatable :: clock
    type(xios_file_type),         allocatable :: filelist(:)

  contains
    private
    procedure, public :: initialise
    procedure, public :: get_clock
    procedure, public :: get_filelist
    final :: finalise
  end type lfric_xios_context_type

abstract interface

  subroutine filelist_populator(files_list, clock)
    import xios_file_type, clock_type
    type(xios_file_type), allocatable, intent(out) :: files_list(:)
    class(clock_type),                 intent(in)  :: clock
  end subroutine filelist_populator

end interface

contains

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  !> @brief Set up an XIOS context object.
  !>
  !> @param [in]     id                Unique identifying string.
  !> @param [in]     communicator      MPI communicator used by context.
  !> @param [in,out] callback          Object to handle model specifics.
  !> @param [in]     start_time        Time of first step.
  !> @param [in]     finish_time       Time of last step.
  !> @param [in]     spinup_period     Number of seconds in spinup period.
  !> @param [in]     seconds_per_step  Number of seconds in a time step.
  !> @param [in]     timer_flag        Flag for use of subroutine timers.
  !> @param [in]     populate_filelist Procedure use to populate list of files
  !>
  subroutine initialise( this, id, communicator,  &
                         callback,                &
                         start_time, finish_time, &
                         spinup_period,           &
                         seconds_per_step,        &
                         timer_flag,              &
                         populate_filelist )

    implicit none

    class(lfric_xios_context_type),     intent(inout) :: this
    character(*),                       intent(in)    :: id
    integer(i_native),                  intent(in)    :: communicator
    class(io_context_initialiser_type), intent(inout) :: callback
    character(*),                       intent(in)    :: start_time
    character(*),                       intent(in)    :: finish_time
    real(r_second),                     intent(in)    :: spinup_period
    real(r_second),                     intent(in)    :: seconds_per_step
    logical(l_def), optional,           intent(in)    :: timer_flag
    procedure(filelist_populator),  &
                     pointer, optional, intent(in)    :: populate_filelist

    type(step_calendar_type), allocatable :: calendar
    integer(i_native)                     :: rc

    call xios_context_initialize( id, communicator )
    call xios_get_handle( id, this%handle )
    call xios_set_current_context( this%handle )

    allocate( calendar, stat=rc )
    if (rc /= 0) then
      call log_event( "Unable to allocate calendar", log_level_error )
    end if

    allocate( this%clock, stat=rc )
    if (rc /= 0) then
      call log_event( "Unable to allocate clock", log_level_error )
    end if
    call this%clock%initialise( calendar, start_time, finish_time, &
                                seconds_per_step, spinup_period,   &
                                timer_flag=timer_flag )

    if (present(populate_filelist)) then
      call populate_filelist(this%filelist, this%clock)
    else
      allocate(this%filelist(0))
    end if

    !> @todo Rather than using this callback we might prefer to pass arrays
    !>       of objects which describe things to be set up. Alternatively we
    !>       could provide calls to "add axis" and "add file" with a final
    !>       "complete context".
    !>
    call callback%callback( this )

    call xios_close_context_definition()

  end subroutine initialise

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  !> Clean up an XIOS context object.
  !>
  subroutine finalise( this )

    implicit none

    type(lfric_xios_context_type), intent(in) :: this

    call xios_context_finalize()

  end subroutine finalise

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  !> Gets the clock associated with this context.
  !>
  !> @return Clock object.
  !>
  function get_clock( this ) result(clock)

    implicit none

    class(lfric_xios_context_type), intent(in), target :: this
    class(clock_type), pointer :: clock

    clock => this%clock

  end function get_clock

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  !> Gets the context's file list
  !>
  !> @return  The list of XIOS file type objects used by the model
  !>
  function get_filelist( this ) result( filelist )

    implicit none

    class(lfric_xios_context_type), intent(in) :: this
    type(xios_file_type), allocatable :: filelist(:)

    filelist = this%filelist

  end function get_filelist

end module lfric_xios_context_mod

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