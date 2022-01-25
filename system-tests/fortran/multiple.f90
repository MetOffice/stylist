program multiple_problems

    implicit none

    integer, pointer :: common_bar
    procedure(some_proc_if), pointer :: common_proc

    type test_type
        integer, pointer :: foo
    end type test_type

	! Tab before comment - wrong
    ! Tab in comment	- okay

    write(6,'(A)') "Tabs in strings	are okay too"

end program multiple_problems

module stuff_mod

    type typy_type

    end type typy_type

    integer, pointer :: common_bar
    procedure(some_proc_if), pointer :: common_proc

    type test_type
        integer, pointer :: foo
    end type test_type

contains

    subroutine procy_proc

    end subroutine procy_proc

    function what_is_foo(box)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer :: what_is_foo
        what_is_foo => box%foo
    end function what_is_foo

    subroutine make_it_foo(box, foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer, intent(in) :: foo
        box%foo => foo
    end subroutine make_it_foo

    function what_is_foo_really(box) result(foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer :: foo
        foo => box%foo
    end function what_is_foo_really

    subroutine also_foo(box, foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer, intent(out) :: foo
        foo => box%foo
    end subroutine also_foo

    subroutine finally_foo(box, foo, new_foo)
        class(test_type), intent(in) :: box
        integer, pointer, intent(inout) :: foo
        integer, pointer, intent(in) :: new_foo
        foo = box%foo
        box%foo = new_foo
    end subroutine finally_foo

    function what_is_foo(box)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer :: what_is_foo
        what_is_foo => box%foo
    end function what_is_foo

    subroutine make_it_foo(box, foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer, intent(in) :: foo
        box%foo => foo
    end subroutine make_it_foo

    function what_is_foo_really(box) result(foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer :: foo
        foo => box%foo
    end function what_is_foo_really

    subroutine also_foo(box, foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer, intent(out) :: foo
        foo => box%foo
    end subroutine also_foo

    subroutine finally_foo(box, foo, new_foo)
        implicit none
        class(test_type), intent(in) :: box
        integer, pointer, intent(inout) :: foo
        integer, pointer, intent(in) :: new_foo
        foo = box%foo
        box%foo = new_foo
    end subroutine finally_foo

end module stuff_mod
