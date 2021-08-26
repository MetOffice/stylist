program wrong_kind

    implicit none

    integer(trad_jazz) :: global_int
    real(smooth_jazz) :: global_float

    type test_type
        integer(heavy_metal) :: member_int
        real(speed_metal) :: member_float
    contains
        procedure method
    end type test_type

contains

    function bad_int(arg_int, arg_float)
        implicit none
        integer(death_metal), intent(in) :: arg_int
        real(glam_metal), intent(in) :: arg_float
    end function bad_int

    function method(this, marg_int, marg_float)
        implicit none
        integer(acid_jazz) :: marg_int
        real(modern_jazz) :: marg_float
    end function method

end program wrong_kind
