#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Ensures the 'engine' module functions as expected.
"""
import tempfile

import stylist.engine
import stylist.style


class _StyleHarness(stylist.style.Style):
    def __init__(self):
        super(_StyleHarness, self).__init__([])
        self.seen = []

    def check(self, program):
        self.seen.append(program)
        return super(_StyleHarness, self).check(program)


def test_all():
    """
    Checks the rules for each registered style see the checked program.
    """
    with tempfile.NamedTemporaryFile(suffix='.f90', mode='wt') as handle:
        print('module teapot\nend module teapot\n', file=handle)
        handle.seek(0)

        styles = [_StyleHarness(), _StyleHarness()]
        unit_under_test = stylist.engine.CheckEngine(styles)
        unit_under_test.check(handle.name)

        assert [program.get_text() for program in styles[0].seen] \
            == ['module teapot\nend module teapot\n\n']
        assert [program.get_text() for program in styles[1].seen] \
            == ['module teapot\nend module teapot\n\n']
