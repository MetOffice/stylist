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
from typing import List, Sequence, Tuple

import pytest
from pytest import fixture  # type: ignore

_test_dir = Path(__file__).parent / 'simple'


class SystemTest:
    @staticmethod
    def run_system(style: str,
                   files: Sequence[str]) -> Tuple[int, List[str], List[str]]:
        command: List[str] = ['python', '-m', 'stylist',
                              '-configuration',
                              str(_test_dir / 'simple.py'),
                              '-style', style]
        command.extend([str(_test_dir / leafname)
                        for leafname in files])
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        return (process.returncode,
                process.stdout.decode('utf-8').strip().splitlines(),
                process.stderr.decode('utf-8').strip().splitlines())

    @staticmethod
    def get_expected(tag: str) -> Tuple[List[str], List[str]]:
        expected_output: List[str] = []
        expected_error: List[str] = []
        buffer: List[str] = expected_output
        expected_file = _test_dir / f'expected.{tag}.txt'
        for line in expected_file.read_text().splitlines():
            if line == 'stdout':
                buffer = expected_output
            elif line == 'stderr':
                buffer = expected_error
            else:
                buffer.append(line.replace('$$', str(_test_dir)))
        return expected_output, expected_error


class _CaseParam:
    def __init__(self, style: str, name: str, files: List[str], rc: int) \
            -> None:
        self.style = style
        self.name = name
        self.files = files
        self.rc = rc


class TestWhitespace(SystemTest):
    @fixture(scope='class',
             params=[_CaseParam('whitespace', 'Single file, no problem',
                                ['nice.txt'], 0),
                     _CaseParam('whitespace', 'Dual file, no problem',
                                ['nice.txt', 'fluffy.txt'], 0),
                     _CaseParam('whitespace', 'Single file, problem',
                                ['naughty.txt'], 1),
                     _CaseParam('whitespace', 'Dual file, mixed',
                                ['nice.txt', 'naughty.txt'], 1)])
    def case(self, request):
        return request.param

    def test_case(self, case: _CaseParam):
        expected_tag = ''.join([word[0].lower() for word in case.name.split()])
        expected_output, expected_error = self.get_expected(expected_tag)

        return_code, stdout, stderr = self.run_system(case.style, case.files)
        assert return_code == case.rc
        assert stderr == expected_error
        assert stdout == expected_output


class TestLineLength(SystemTest):
    @pytest.fixture(scope='class',
                    params=[('line_length_default', 'lld'),
                            ('line_length_default_indent', 'lldi'),
                            ('line_length_forty', 'll40'),
                            ('line_length_forty_indent', 'll40i'),
                            ('line_length_120', 'll120'),
                            ('line_length_120_indent', 'll120i')])
    def case(self, request):
        return request.param

    def test_line_length(self, case):
        expected_output, expected_error = self.get_expected(case[1])

        return_code, stdout, stderr = self.run_system(case[0],
                                                      ['line_length.txt'])
        assert return_code != 0
        assert stderr == expected_error
        assert stdout == expected_output
