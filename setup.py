"""Setup Stylist for distribution on PyPI."""

import os
from setuptools import setup, find_packages

# Get the long description from the README file
with open(
    os.path.join(os.path.dirname(__file__), 'README.md'),
    encoding='utf-8',
) as handle:
    LONG_DESCRIPTION = handle.read()

setup(
    name='stylist',
    # TODO:
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',
    description=(
        'Extensible code style checker'
        ' currently supporting Fortran, PSyclone DSL, etc'
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/MetOffice/stylist',
    author='Met Office',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='linter fortran psyclone',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=['fparser'],
    extras_require={
        'dev': ['check-manifest', 'flake8'],
        'test': ['pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': ['stylist=stylist.__main__:main'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/MetOffice/stylist/issues',
        'Source': 'https://github.com/MetOffice/stylist/',
    },
)
