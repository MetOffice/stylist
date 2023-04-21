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
import logging
from os import linesep
from pathlib import Path
import sys
from textwrap import indent
from typing import List, Sequence

from stylist import StylistException
from stylist.configuration import (Configuration,
                                   ConfigTools,
                                   load_configuration)
from stylist.engine import CheckEngine
from stylist.issue import Issue
from stylist.source import SourceFactory
from stylist.style import Style


def _parse_cli() -> argparse.Namespace:
    """
    Parse the command line for stylist arguments.
    """
    description = 'Perform various code style checks on source code.'

    max_key_len: int = max(len(key) for key in ConfigTools.language_keys())
    parsers = [key.ljust(max_key_len)
               + ' - '
               + ConfigTools.language(key).get_name()
               for key in ConfigTools.language_keys()]
    max_key_len = max(len(key) for key in ConfigTools.preprocessor_keys())
    preproc = [key.ljust(max_key_len)
               + ' - '
               + ConfigTools.preprocessor(key).get_name()
               for key in ConfigTools.preprocessor_keys()]
    epilog = f"""
IDs used in specifying extension pipelines:
  Parsers:
{indent(linesep.join(parsers), '    ')}
  Preprocessors:
{indent(linesep.join(preproc), '    ')}
"""
    formatter_class = argparse.RawDescriptionHelpFormatter
    cli_parser = argparse.ArgumentParser(prog="stylist",
                                         add_help=False,
                                         description=description,
                                         epilog=epilog,
                                         formatter_class=formatter_class)
    cli_parser.add_argument('-help', '-h', '--help', action='help')
    cli_parser.add_argument('-verbose', action="store_true",
                            help="Produce a running commentary on progress.")
    cli_parser.add_argument('-configuration',
                            type=Path,
                            metavar='FILENAME',
                            help="File which configures the tool.")
    message = "Style to use for check. May be specified repeatedly."
    cli_parser.add_argument('-style',
                            action='append',
                            metavar='NAME',
                            help=message)
    message = 'Add a mapping between file extension and pipeline'
    cli_parser.add_argument('-map-extension',
                            metavar='EXTENSION:PARSER[:PREPROCESSOR]...',
                            dest='map_extension',
                            default=[],
                            action='append',
                            help=message)
    cli_parser.add_argument('source', metavar='FILE', nargs='+',
                            type=Path,
                            help='Filename of source file or directory')

    arguments = cli_parser.parse_args()

    return arguments


def _process(candidates: List[Path], styles: Sequence[Style]) -> List[Issue]:
    """
    Examines files for style compliance.

    Any directories specified will be descended looking for files to examine.
    """
    engine = CheckEngine(styles)

    hot_extensions = SourceFactory.get_extensions()

    issues: List[Issue] = []
    while candidates:
        file_object = candidates.pop(0)
        if file_object.is_dir():
            for leaf_filename in file_object.iterdir():
                if leaf_filename.suffix[1:] in hot_extensions \
                   or leaf_filename.is_dir():
                    candidates.append(leaf_filename)
        else:  # Is a file
            issues.extend(engine.check(file_object))

    return issues


def _configure(project_file: Path) -> Configuration:
    configuration = load_configuration(project_file)
    # TODO /etc/fab.ini
    # TODO ~/.fab.ini - Path.home() / '.fab.ini'
    return configuration


def main() -> None:
    """
    Command-line tool entry point.
    """
    logger = logging.getLogger('stylist')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    arguments = _parse_cli()

    if arguments.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    configuration = _configure(arguments.configuration)

    styles = []
    if arguments.style is None:
        if len(configuration.styles) == 1:
            for style in configuration.styles.values():
                styles.append(style)
        else:
            message = "No style specified and more than one defined."
            raise StylistException(message)
    else:
        for name in arguments.style:
            styles.append(configuration.styles[name])

    # Pipelines loaded from configuration file
    #
    for extension, pipe in configuration.file_pipes.items():
        SourceFactory.add_extension(extension, pipe)
    #
    # Pipelines from command line.
    #
    for mapping in arguments.map_extension:
        extension, pipe = ConfigTools.parse_pipe_description(mapping)
        SourceFactory.add_extension(extension, pipe)

    issues = _process(arguments.source, styles)

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
