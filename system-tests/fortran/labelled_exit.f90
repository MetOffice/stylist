program test_program
    integer :: i, j
    a : do i = 1, 3
        exit
    end do a
    b : do i = 1, 3
        exit b
    end do b
    c : do i = 1, 3
        if (i==2) exit
    end do c
    d : do i = 1, 3
        if (i==2) exit d
    end do d
end program test_program