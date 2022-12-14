##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Benchmark performance of all rules on some real-world code.
"""
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from json import load as json_load
from math import nan
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt  # type: ignore
import pytest

from stylist.source import FortranSource, SourceFileReader
from stylist.style import Style


@pytest.mark.benchmark(group='fortran-style')
def test_fortran_style(perf_source_file: Path,
                       fortran_style: Style,
                       benchmark):
    benchmark.extra_info['fortran-source'] = perf_source_file.name
    benchmark.extra_info['timestamp'] = datetime.now().timestamp()
    test_file = SourceFileReader(perf_source_file)
    fortran_source = FortranSource(test_file)
    _ = benchmark(fortran_style.check, fortran_source)


AVERAGE_WINDOW = 3


def plot_style_time_series(results_dir: Path, plot_file: Optional[Path]):
    series: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
    for results_file in results_dir.iterdir():
        with results_file.open('rt') as handle:
            results = json_load(handle)
            for bench in results['benchmarks']:
                if bench['group'] == 'fortran-style':
                    extra_info = bench['extra_info']
                    timestamp = datetime.fromtimestamp(extra_info['timestamp'])
                    minimum = float(bench['stats']['min'])
                    new_datum = (timestamp, minimum)
                    series[extra_info['fortran-source']].append(new_datum)

    figure, axes = plt.subplots()
    figure.set_size_inches(8, 6)
    for experiment, readings in series.items():
        stamps = [datum[0] for datum in readings]
        data = [datum[1] for datum in readings]
        average = []
        i = 0
        while i < len(data) - AVERAGE_WINDOW + 1:
            window = data[i:i + AVERAGE_WINDOW]
            window_average = sum(window) / AVERAGE_WINDOW
            average.append(window_average)
            i += 1
        while i < len(data):
            average.append(nan)
            i += 1
        axes.scatter(stamps, data, label=experiment)
        axes.plot(stamps, average)
    plt.title("All Fortran Rules")
    plt.ylabel("Duration (s)")
    plt.xlabel("Time of run")
    figure.autofmt_xdate()
    plt.legend()
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
    plot_style_time_series(arguments.results_dir, arguments.plot_file)
