module stuff_mod

    type typy_type

    end type typy_type

contains

    subroutine procy_proc

    end subroutine procy_proc

end module stuff_mod


program missing_implicit

    use stuff_mod, only : typy_type

end program missing_implicit