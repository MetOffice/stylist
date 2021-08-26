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
from typing import List, Tuple

from pytest import fixture  # type: ignore
# ToDo: Obviously we shouldn't be importing "private" modules but until pytest
#       sorts out its type hinting we are stuck with it.
#
from _pytest.fixtures import FixtureRequest  # type: ignore


class TestFortranRules(object):
    _RULES = ['bad_character',
              'missing_implicit',
              'missing_only',
              'missing_pointer_init',
              'wrong_kind']

    @fixture(scope='class', params=_RULES)
    def rule(self, request: FixtureRequest) -> str:
        return request.param

    @staticmethod
    def _get_expected(test_dir: Path,
                      name: str) -> Tuple[List[str], List[str]]:
        expected_output: List[str] = []
        expected_error: List[str] = []
        buffer: List[str] = expected_output
        expected_file = test_dir / f'expected.{name}.txt'
        for line in expected_file.read_text().splitlines(keepends=True):
            if line == 'stdout\n':
                buffer = expected_output
            elif line == 'stderr\n':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(test_dir)))
        return expected_output, expected_error

    def test_rule(self, rule: str) -> None:
        test_dir = Path(__file__).parent / 'fortran'

        expected_output, expected_error \
            = TestFortranRules._get_expected(test_dir, rule)

        command: List[str] = ['python', '-m', 'stylist',
                              '-configuration',
                              str(test_dir / 'configuration.ini'),
                              '-style', rule,
                              str(test_dir / f'{rule}.f90')]
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        assert process.returncode == 1
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()

    def test_all(self) -> None:
        test_dir = Path(__file__).parent / 'fortran'

        expected_output, expected_error \
            = TestFortranRules._get_expected(test_dir, 'all')

        command: List[str] = ['python', '-m', 'stylist',
                              '-configuration',
                              str(test_dir / 'configuration.ini'),
                              '-style', 'all']
        for rule in TestFortranRules._RULES:
            command.append(str(test_dir / f'{rule}.f90'))
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        assert process.returncode == 1
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()
