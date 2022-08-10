##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
System test of Fortran rules.
"""
from collections import namedtuple
import re
from pathlib import Path
import subprocess
from typing import Generator, List, Optional, Tuple

from pytest import fixture  # type: ignore

_CASE_TUPLE = namedtuple('_CASE_TUPLE', ['test', 'variant'])
_STYLE_PATTERN = re.compile(r'\s*(.+?)\s*=\s*Style\(')


def _list_cases() -> List[_CASE_TUPLE]:
    test_dir = Path(__file__).parent / 'fortran'
    config_file = test_dir / 'fortran.py'
    tests: List[_CASE_TUPLE] = list()
    for line in config_file.read_text().splitlines():
        match = _STYLE_PATTERN.match(line)
        if match:
            style = match.group(1)
            test, _, variant = style.partition('__')
            if not variant:
                variant = None
            case = _CASE_TUPLE(test, variant)
            tests.append(case)
    tests.sort(key=lambda x: f"{x.test}#{x.variant}")
    return tests


class TestFortranRules(object):
    @fixture(scope='class', params=_list_cases())
    def case(self, request) -> Generator[_CASE_TUPLE, None, None]:
        yield request.param

    @staticmethod
    def _get_expected(test_dir: Path,
                      name: str) -> Tuple[List[str], List[str]]:
        expected_output: List[str] = []
        expected_error: List[str] = []
        buffer: List[str] = expected_output
        expected_file = test_dir / f'expected.{name.replace("__", "#")}.txt'
        for line in expected_file.read_text().splitlines(keepends=True):
            if line == 'stdout\n':
                buffer = expected_output
            elif line == 'stderr\n':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(test_dir)))
        return expected_output, expected_error

    def test_single_rules(self, case: Tuple[str, Optional[str], str]) -> None:
        test = case[0]
        variant = case[1]

        if variant is None:
            case_name = test
        else:
            case_name = f"{test}__{variant}"

        test_dir = Path(__file__).parent / 'fortran'

        expected_output, expected_error \
            = TestFortranRules._get_expected(test_dir, case_name)

        command: List[str] = ['python', '-m', 'stylist',
                              '-configuration',
                              str(test_dir / 'fortran.py'),
                              '-style', case_name,
                              str(test_dir / f'{test}.f90')]
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        assert process.returncode != 0
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()
