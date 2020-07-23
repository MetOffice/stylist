#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Tool for checking code style.
"""
import argparse
from io import StringIO
import logging
import os.path
from pathlib import Path
import sys
from typing import Iterable, List, Mapping, Sequence, Type

from stylist.engine import CheckEngine
from stylist.issue import Issue
from stylist.source import CPreProcessor, CSource, FortranPreProcessor, \
                           FortranSource, PFUnitProcessor, PlainText, \
                           SourceFactory, SourceTree, TextProcessor
from stylist.style import read_style, Style


def parse_cli() -> argparse.Namespace:
    """
    Parse the command line for stylist arguments.
    """
    description = 'Perform various code style checks on source code.'

    max_key_length: int = max(len(key) for key in _LANGUAGE_MAP.keys())
    parsers = [key.ljust(max_key_length) + ' - ' + str(parser)
               for key, parser in _LANGUAGE_MAP.items()]
    max_key_length = max(len(key) for key in _PREPROCESSOR_MAP.keys())
    preproc = [key.ljust(max_key_length) + ' - ' + str(proc)
               for key, proc in _PREPROCESSOR_MAP.items()]
    epilog = """"\
IDs used in specifying extension pipelines:
  Parsers:
    {parsers}
  Preprocessors:
    {preproc}
    """.format(parsers='\n    '.join(parsers),
               preproc='\n    '.join(preproc))
    formatter_class = argparse.RawDescriptionHelpFormatter
    cli_parser = argparse.ArgumentParser(add_help=False,
                                         description=description,
                                         epilog=epilog,
                                         formatter_class=formatter_class)
    cli_parser.add_argument('-help', '-h', '--help', action='help')
    cli_parser.add_argument('-verbose', '-v', action="store_true",
                            help="Produce a running commentary on progress.")
    cli_parser.add_argument('-configuration',
                            type=Path,
                            default=None,
                            metavar='FILENAME',
                            help="File which configures the tool.")
    help = "Style to use for check. May be specified repeatedly."
    cli_parser.add_argument('-style',
                            action='append',
                            metavar='NAME',
                            help=help)
    message = 'Add a mapping between file extension and pipeline'
    cli_parser.add_argument('-map-extension',
                            metavar='EXTENSION:PARSER[:PREPROCESSOR]',
                            dest='map_extension',
                            default=[],
                            action='append',
                            help=message)
    cli_parser.add_argument('source', metavar='FILE', nargs='+',
                            help='Filename of source file or directory')

    arguments = cli_parser.parse_args()

    if arguments.configuration is None:
        arguments.configuration = StringIO('')

    return arguments


_LANGUAGE_MAP: Mapping[str, Type[SourceTree]] \
    = {'c': CSource,
       'cxx': CSource,
       'fortran': FortranSource,
       'text': PlainText}
_PREPROCESSOR_MAP: Mapping[str, Type[TextProcessor]] \
    = {'cpp': CPreProcessor,
       'fpp': FortranPreProcessor,
       'pfp': PFUnitProcessor}


def _add_extensions(additional_extensions: Iterable[str]) -> None:
    """
    Makes the package aware of new extensions and how to deal with them.

    This includes a few used by the LFRic project. Obviously these should not
    be hard coded in here.
    """
    # This application always expects pFUnit source to be present so it adds
    # a rule for that.
    #
    SourceFactory.add_extension('pf',
                                FortranSource,
                                PFUnitProcessor)
    SourceFactory.add_extension('PF',
                                FortranSource,
                                FortranPreProcessor,
                                PFUnitProcessor)
    # PSyclone algorithms are also expected. By design these are actually
    # syntactically correct Fortran so they are treated exactly as Fortran
    # files are. In particular, they are treated like .F90 files as
    # preprocessor directives may appear in them.
    #
    SourceFactory.add_extension('x90',
                                FortranSource,
                                FortranPreProcessor)
    # It can be useful to process plain text files for debugging purposes.
    SourceFactory.add_extension('txt', PlainText)

    for mapping in additional_extensions:
        extension, language, preprocessors = mapping.split(':', 2)
        preproc_objects = [_PREPROCESSOR_MAP[ident.lower()]
                           for ident in preprocessors.split(':')]
        SourceFactory.add_extension(extension.lower(),
                                    _LANGUAGE_MAP[language.lower()],
                                    *preproc_objects)


def process(candidates: List[str], styles: Sequence[Style]) -> List[Issue]:
    """
    Examines files for style compliance.

    Any directories specified will be descended looking for files to examine.
    """
    engine = CheckEngine(styles)

    hot_extensions = SourceFactory.get_extensions()

    issues: List[Issue] = []
    while candidates:
        filename = candidates.pop(0).strip()
        if os.path.isdir(filename):
            for leaf in os.listdir(filename):
                leaf_filename = os.path.join(filename, leaf)
                _, extension = os.path.splitext(leaf_filename)
                if extension[1:] in hot_extensions \
                   or os.path.isdir(leaf_filename):
                    candidates.append(leaf_filename)
        else:  # Is a file
            issues.extend(engine.check(filename))

    return issues


def main() -> None:
    """
    Command-line tool entry point.
    """
    logger = logging.getLogger('stylist')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    arguments = parse_cli()

    if arguments.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    styles = []
    for name in arguments.style:
        styles.append(read_style(arguments.configuration, name))

    _add_extensions(arguments.map_extension)

    issues = process(arguments.source, styles)

    for issue in issues:
        print(str(issue), file=sys.stderr)
    if (len(issues) > 0) or arguments.verbose:
        tally = len(issues)
        if tally > 1:
            plural = 's'
        else:
            plural = ''
        print(f"Found {tally} issue{plural}")

    if issues:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
