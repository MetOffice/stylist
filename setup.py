"""Setup Stylist for distribution on PyPI."""

from ast import literal_eval
from pathlib import Path
from setuptools import setup, find_packages  # type: ignore

# Get the long description from the README file
HERE = Path(__file__).parent
with (HERE / 'source/stylist/__init__.py').open(encoding='utf-8') as handle:
    for line in handle:
        items = line.split('=', 1)
        if items[0].strip() == '__version__':
            VERSION = literal_eval(items[1].strip())
            break
    else:
        raise RuntimeError('Cannot determine package version.')

setup(
    version=VERSION,
    package_dir={'': 'source'},
    packages=find_packages(where='source'),
    python_requires='>=3.7, <4',
    install_requires=['fparser >= 0.0.12'],
    extras_require={
        'dev': ['check-manifest', 'flake8', 'mypy'],
        'test': ['pytest', 'pytest-cov'],
        'docs': ['sphinx',
                 'sphinx-autodoc-typehints',
                 'sphinx-rtd-theme'],
        'release': ['setuptools', 'wheel', 'twine']
    },
    entry_points={
        'console_scripts': ['stylist=stylist.__main__:main'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/MetOffice/stylist/issues',
        'Source': 'https://github.com/MetOffice/stylist/',
    },
)
