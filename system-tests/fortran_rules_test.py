#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
System test of Fortran rules.
"""
from pathlib import Path
import subprocess
from typing import List

from pytest import fixture  # type: ignore


class TestFortranRules(object):
    @fixture(scope='class', params=['bad_character',
                                    'missing_implicit',
                                    'missing_only'])
    def rule(self, request):
        return request.param

    def test_rule(self, rule):
        test_dir = Path(__file__).parent / 'fortran'

        expected_output = []
        expected_error = []
        buffer = expected_output
        expected_file = test_dir / f'expected.{rule}.txt'
        for line in expected_file.read_text().splitlines(keepends=True):
            if line == 'stdout\n':
                buffer = expected_output
            elif line == 'stderr\n':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(test_dir)))

        command = ['python', '-m', 'stylist',
                   '-configuration', test_dir / 'configuration.ini',
                   '-style', rule,
                   test_dir / f'{rule}.f90']
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        print(process.stdout)
        assert process.returncode == 1
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
