#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the 'engine' module functions as expected.
"""
from pathlib import Path
import tempfile
from typing import List

from stylist.engine import CheckEngine
from stylist.issue import Issue
from stylist.source import SourceTree
from stylist.style import Style


class _StyleHarness(Style):
    def __init__(self) -> None:
        super().__init__()
        self.seen: List[SourceTree] = []

    def check(self, program: SourceTree) -> List[Issue]:
        self.seen.append(program)
        return super(_StyleHarness, self).check(program)


def test_all_styles() -> None:
    """
    Checks the rules for each registered style see the checked program.
    """
    with tempfile.NamedTemporaryFile(suffix='.f90', mode='wt') as handle:
        print('module teapot\nend module teapot\n', file=handle)
        handle.seek(0)

        styles = [_StyleHarness(), _StyleHarness()]
        unit_under_test = CheckEngine(styles)
        unit_under_test.check(handle.name)

        assert [program.get_text() for program in styles[0].seen] \
            == ['module teapot\nend module teapot\n\n']
        assert [program.get_text() for program in styles[1].seen] \
            == ['module teapot\nend module teapot\n\n']
