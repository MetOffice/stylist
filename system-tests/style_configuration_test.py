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
from typing import List

from pytest import fixture  # type: ignore


class _CaseParam:
    def __init__(self, style: str, name: str, files: List[str], rc: int) \
            -> None:
        self.style = style
        self.name = name
        self.files = files
        self.rc = rc


class TestSystem(object):
    @fixture(scope='class',
             params=[_CaseParam('simple', 'Single file, no problem',
                                ['nice.txt'], 0),
                     _CaseParam('simple', 'Dual file, no problem',
                                ['nice.txt', 'fluffy.txt'], 0),
                     _CaseParam('simple', 'Single file, problem',
                                ['naughty.txt'], 1),
                     _CaseParam('simple', 'Dual file, mixed',
                                ['nice.txt', 'naughty.txt'], 1)])
    def case(self, request):
        return request.param

    def test_case(self, case: _CaseParam):
        test_dir = Path(__file__).parent / case.style

        expected_tag = ''.join([word[0].lower() for word in case.name.split()])
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
                              str(test_dir / 'simple.py'),
                              '-style', case.style]
        command.extend([str(test_dir / leafname) for leafname in case.files])
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        assert process.returncode == case.rc
        assert process.stderr.decode('utf-8').strip() \
            == ''.join(expected_error).strip()
        assert process.stdout.decode('utf-8').strip() \
            == ''.join(expected_output).strip()
