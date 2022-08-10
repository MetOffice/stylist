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

from stylist.fortran import LabelledDoExit
from stylist.source import FortranSource, SourceStringReader


class TestLabelledExit(object):
    """
    Tests the checker of missing exit labels.
    """

    @pytest.fixture(scope='class',
                    params=['', 'foo'])
    def do_construct_name(self, request):
        """
        Parameter fixture giving do construct names to exit statement
        """
        return request.param

    def test_exit_labels(self,
                         do_construct_name: str) -> None:
        """
        Checks that the rule reports missing exit labels correctly.
        """
        template = '''
program test
contains
    function function1()
        foo : do
            exit {do_construct_name}
        end do foo
    end function function1

    function function2()
        foo : do
            if (.true.) exit {do_construct_name}
        end do foo
    end function function2
end program test
'''

        expectation: List[str] = []
        message = '{line}: Usage of "exit" without label indicating which ' \
                  '"do" construct is being exited from.'
        if do_construct_name == '':
            expectation.extend([
                message.format(line=6),
                message.format(line=12)
            ])
        text = template.format(
            do_construct_name=do_construct_name)
        print(text)  # Shows up in failure reports, for debugging
        reader = SourceStringReader(text)
        source = FortranSource(reader)
        unit_under_test = LabelledDoExit()
        issues = unit_under_test.examine(source)
        issue_descriptions = [str(issue) for issue in issues]
        assert issue_descriptions == expectation
