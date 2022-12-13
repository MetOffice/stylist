##############################################################################
# (c) Crown copyright 2022 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Benchmark performance of all rules on some real-world code.
"""
from collections import defaultdict
from datetime import datetime
from json import load as json_load
from math import nan
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
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


def plot_style_time_series(results_dir: Path):
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

    AVERAGE_WINDOW = 3
    figure, axes = plt.subplots()
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
    plt.show()


if __name__ == '__main__':
    results_dir = Path() / '.benchmarks' / 'Linux-CPython-3.7-64bit'
    plot_style_time_series(results_dir)
