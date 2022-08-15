#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Test of the rule for missing exit labels.
"""
from typing import List

import pytest  # type: ignore

from stylist.fortran import IntrinsicModule
from stylist.source import FortranSource, SourceStringReader


# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.


class TestIntrinsicModule(object):
    """
    Tests the checker of missing exit labels.
    """

    @pytest.fixture(scope='class',
                    params=["iso_c_binding", "ISO_Fortran_env",
                            "ieee_exceptions", "ieee_arithmetic",
                            "ieee_features", "other_module"])
    def module_name(self, request):
        """
        Parameter fixture giving module names
        """
        return request.param

    def test_exit_labels(self,
                         module_name: str) -> None:
        """
        Checks that the rule reports missing "implicit" labels correctly
        """
        template = '''
program test
contains
    function function1()
        use {module_name}
    end function function1

    function function2()
        use, intrinsic :: {module_name}
    end function function2
end program test
'''

        expectation: List[str] = []
        message = '{line}: Usage of intrinsic module "{module_name}" without '\
                  '"intrinsic" clause.'
        if module_name.lower() in ["iso_c_binding", "iso_fortran_env",
                                   "ieee_exceptions", "ieee_arithmetic",
                                   "ieee_features"]:
            expectation.extend([
                message.format(line=5, module_name=module_name),
            ])
        text = template.format(
            module_name=module_name)
        print(text)  # Shows up in failure reports, for debugging
        reader = SourceStringReader(text)
        source = FortranSource(reader)
        unit_under_test = IntrinsicModule()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
