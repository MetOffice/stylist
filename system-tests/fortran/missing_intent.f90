program test_program

contains
    function test_function(foo, bar, foobar, baz, qux, bazz) result(quux)

        implicit none

        integer, pointer :: foo
        character, target :: bar, foobar
        real, intent(in) :: BAZ(5)
        logical, intent(in), target :: qux
        logical :: quux

    end function test_function

end program test_program

module test_module

contains

  subroutine test_subroutine( foo, bar, foobar, baz, qux )

      implicit none

      integer, intent(in), pointer :: foo
      character, intent(inout):: bar, foobar
      real :: BAZ(5)
      logical, intent(out):: qux
      logical, pointer :: quux => null()

  end subroutine test_subroutine

end module test_module