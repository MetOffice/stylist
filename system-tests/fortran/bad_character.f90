program bad_character

    implicit none

	! Tab before comment - wrong
    ! Tab in comment	- okay

    write(6,'(A)') "Tabs in strings	are okay too"

end program bad_character
