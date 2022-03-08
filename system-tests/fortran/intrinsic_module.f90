program bad_program
    use iso_c_binding
    use iso_fortran_env
    use ieee_exceptions
    use ieee_arithmetic
    use ieee_features
    use some_module
end program bad_program

module good_module
    use, intrinsic :: iso_c_binding
    use, intrinsic :: iso_c_binding
    use, intrinsic :: ISO_Fortran_env
    use, intrinsic :: ieee_exceptions
    use, intrinsic ::  ieee_arithmetic
    use, intrinsic ::  ieee_features
end module good_module