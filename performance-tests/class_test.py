##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Benchmark performance of individual rules on some real-world code.
"""
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from json import load as json_load
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt
import pytest

from stylist.fortran import FortranRule
from stylist.source import SourceFileReader, FortranSource


@pytest.mark.benchmark(group='fortran-rule')
def test_fortran_rule(perf_source_file: Path,
                      fortran_rule: FortranRule,
                      benchmark):
    benchmark.extra_info['fortran-source'] = perf_source_file.name
    benchmark.extra_info['fortran-rule'] = fortran_rule.__class__.__name__
    benchmark.extra_info['timestamp'] = datetime.now().timestamp()
    test_file = SourceFileReader(perf_source_file)
    fortran_source = FortranSource(test_file)
    _ = benchmark(fortran_rule.examine, fortran_source)


def plot_rule_time_series(results_dir: Path, plot_file: Optional[Path]):
    series: Dict[str, Dict[str, List[Tuple[datetime, float]]]] \
        = defaultdict(lambda: defaultdict(list))
    for results_file in results_dir.iterdir():
        with results_file.open('rt') as handle:
            results = json_load(handle)
            for bench in results['benchmarks']:
                if bench['group'] == 'fortran-rule':
                    extra_info = bench['extra_info']
                    timestamp = datetime.fromtimestamp(extra_info['timestamp'])
                    source = extra_info['fortran-source']
                    rule = extra_info['fortran-rule']
                    minimum = float(bench['stats']['min'])
                    new_datum = (timestamp, minimum)
                    series[source][rule].append(new_datum)

    figure, uber_axes = plt.subplots(2, 2, layout='constrained')
    figure.set_size_inches(12, 8)
    axes_index = 0
    for experiment, rules in series.items():
        axes = uber_axes.flat[axes_index]
        axes_index += 1
        for rule, readings in rules.items():
            stamps = [datum[0] for datum in readings]
            data = [datum[1] for datum in readings]
            axes.scatter(stamps, data, label=rule)
        title = f"Time to run rule against source file {experiment}"
        axes.set_title(title)
        axes.set_ylabel("Duration (s)")
        axes.set_xlabel("Time of run")
        if axes_index == 1:
            axes.legend(loc='best')
    if plot_file is not None:
        figure.savefig(plot_file, transparent=False, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':
    default_results_dir = Path() / '.benchmarks' / 'Linux-CPython-3.7-64bit'
    cli_parser = ArgumentParser()
    cli_parser.add_argument('-results_dir', type=Path,
                            default=default_results_dir)
    cli_parser.add_argument('-plot_file', type=Path, default=None)
    arguments = cli_parser.parse_args()
    plot_rule_time_series(arguments.results_dir, arguments.plot_file)
