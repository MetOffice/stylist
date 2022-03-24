program a_program
    use iso_c_binding
    use, intrinsic :: iso_fortran_env
    use ieee_exceptions
    use ieee_arithmetic
    use, intrinsic :: ieee_features
    use some_module
end program a_program

module a_module
    use, intrinsic :: iso_c_binding
    use ISO_Fortran_env
    use, intrinsic :: ieee_exceptions
    use, intrinsic :: ieee_arithmetic
    use ieee_features
    use some_module
end module a_module

function a_function(x)
    use iso_c_binding
    use, intrinsic :: iso_fortran_env
    use ieee_exceptions
    use ieee_arithmetic
    use, intrinsic :: ieee_features
    use some_module
    integer, intent(inout) :: x = 2
end function

subroutine a_subroutine
    use, intrinsic :: iso_c_binding
    use ISO_Fortran_env
    use, intrinsic :: ieee_exceptions
    use, intrinsic :: ieee_arithmetic
    use ieee_features
    use some_module
end subroutine
