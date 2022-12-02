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
