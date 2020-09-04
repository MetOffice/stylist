#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
System tests using a style from configuration.
"""
from pathlib import Path
import subprocess
from typing import List, Tuple

from pytest import fixture  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore


class TestSystem(object):
    @fixture(scope='class',
             params=[('simple', 'Single file, no problem', ['nice.txt'], 0),
                     ('simple', 'Dual file, no problem', ['nice.txt',
                                                          'fluffy.txt'], 0),
                     ('simple', 'Single file, problem', ['naughty.txt'], 1),
                     ('simple', 'Dual file, mixed', ['nice.txt',
                                                     'naughty.txt'], 1)])
    def case(self, request: FixtureRequest) \
            -> Tuple[str, str, List[str], int]:
        return request.param

    def test_case(self, case: Tuple[str, str, List[str], int]):
        test_style: str = case[0]
        test_name: str = case[1]
        test_files: List[str] = case[2]
        expected_rc: int = case[3]

        test_dir = Path(__file__).parent / test_style

        expected_tag = ''.join([word[0].lower() for word in test_name.split()])
        expected_output: List[str] = []
        expected_error: List[str] = []
        buffer: List[str] = expected_output
        expected_file = test_dir / f'expected.{expected_tag}.txt'
        for line in expected_file.read_text().splitlines(keepends=True):
            if line == 'stdout\n':
                buffer = expected_output
            elif line == 'stderr\n':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(test_dir)))

        command: List[str] = ['python', '-m', 'stylist',
                              '-configuration',
                              str(test_dir / 'configuration.ini'),
                              '-style', test_style]
        command.extend([str(test_dir / leafname) for leafname in test_files])
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        assert process.returncode == expected_rc
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()
