#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
System tests simple operation.
"""
from pathlib import Path
import subprocess
from typing import List

from pytest import fixture  # type: ignore


class TestSystem(object):
    @fixture(scope='class',
             params=[('simple', 'Single file, no problem', ['nice.txt'])])
    def case(self, request):
        yield request.param

    def test_case(self, case):
        test_style: str = case[0]
        test_name: str = case[1]
        test_files: List[str] = case[2]

        test_dir = Path(__file__).parent / test_style

        expected_tag = ''.join([word[0].lower() for word in test_name.split()])
        expected_output = []
        expected_error = []
        buffer = expected_output
        expected_file = test_dir / f'expected.{expected_tag}.txt'
        for line in expected_file.read_text().splitlines():
            if line == 'stdout':
                buffer = expected_output
            elif line == 'stderr':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(test_dir)))

        command = ['python', '-m', 'stylist',
                   '-configuration', test_dir / 'configuration.ini',
                   '-style', test_style]
        command.extend([test_dir / leafname for leafname in test_files])
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        assert process.returncode == 0
        assert process.stdout.decode('utf-8').strip() \
            == '\n'.join(expected_output)
        assert process.stderr.decode('utf-8').strip() \
            == '\n'.join(expected_error)
