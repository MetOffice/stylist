##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Extensions to the PyTest framework.
"""
import inspect
from pathlib import Path
from re import compile as re_compile
from shutil import unpack_archive
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Type

import stylist.fortran
from stylist.fortran import FortranRule
from stylist.rule import Rule
from stylist.style import Style


def pytest_sessionstart(session):
    session.config._temp_dir = TemporaryDirectory()
    unpack_archive('performance-tests/examples.tar', session.config._temp_dir.name)
    session.config._perf_source_files = []
    dir = Path(session.config._temp_dir.name)
    for file in list(dir.iterdir()):
        if file.is_file():
            session.config._perf_source_files.append(file)


def pytest_sessionfinish(session):
    session.config._temp_dir.cleanup()


_RULE_CONSTRUCTION: Dict[Type[FortranRule], Dict[str, Any]] = {
    stylist.fortran.ForbidUsage:
        {'name': 'mpi'},
    stylist.fortran.KindPattern:
        {'integer': re_compile(r'i_.+'),
         'real': re_compile(r'r_.+')}
}


def pytest_generate_tests(metafunc):
    if 'perf_source_file' in metafunc.fixturenames:
        files = metafunc.config._perf_source_files
        metafunc.parametrize('perf_source_file',
                             files,
                             ids=[file.name for file in files])

    if 'fortran_rule' in metafunc.fixturenames \
            or 'fortran_style' in metafunc.fixturenames:
        rules: List[FortranRule] = []
        for _, cls in inspect.getmembers(stylist.fortran, inspect.isclass):
            if issubclass(cls, FortranRule) and cls != FortranRule:
                kwargs = _RULE_CONSTRUCTION.get(cls)
                if kwargs is None:
                    kwargs = {}
                rules.append(cls(**kwargs))
        if 'fortran_rule' in metafunc.fixturenames:
            metafunc.parametrize('fortran_rule',
                                 rules,
                                 ids=[rule.__class__.__name__ for rule in rules])
        if 'fortran_style' in metafunc.fixturenames:
            metafunc.parametrize('fortran_style',
                                 [Style(*rules)])

    if 'text_rule' in metafunc.fixturenames:
        rules: List[Type[Rule]] = []
        for _, cls in inspect.getmembers(stylist.rule, inspect.isclass):
            if issubclass(cls, Rule) and cls != Rule:
                rules.append(cls)
        metafunc.parametrize('text_rule',
                             rules,
                             ids=[rule.__name__ for rule in rules])
