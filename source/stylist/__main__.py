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
import os.path
from pathlib import Path
import sys
from typing import List, Sequence

from stylist.configuration import Configuration, ConfigurationFile
from stylist.engine import CheckEngine
from stylist.issue import Issue
from stylist.source import SourceFactory
from stylist.style import determine_style, Style


def _parse_cli() -> argparse.Namespace:
    """
    Parse the command line for stylist arguments.
    """
    description = 'Perform various code style checks on source code.'

    max_key_len: int = max(len(key) for key in Configuration.language_tags())
    parsers = [key.ljust(max_key_len)
               + ' - '
               + str(Configuration.language_lookup(key))
               for key in Configuration.language_tags()]
    max_key_len = max(len(key) for key in Configuration.preprocessor_tags())
    preproc = [key.ljust(max_key_len)
               + ' - '
               + str(Configuration.preprocessor_lookup(key))
               for key in Configuration.preprocessor_tags()]
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
    cli_parser.add_argument('-verbose', action="store_true",
                            help="Produce a running commentary on progress.")
    cli_parser.add_argument('-configuration',
                            type=Path,
                            metavar='FILENAME',
                            help="File which configures the tool.")
    help = "Style to use for check. May be specified repeatedly."
    cli_parser.add_argument('-style',
                            action='append',
                            metavar='NAME',
                            help=help)
    message = 'Add a mapping between file extension and pipeline'
    cli_parser.add_argument('-map-extension',
                            metavar='EXTENSION:PARSER[:PREPROCESSOR]...',
                            dest='map_extension',
                            default=[],
                            action='append',
                            help=message)
    cli_parser.add_argument('source', metavar='FILE', nargs='+',
                            help='Filename of source file or directory')

    arguments = cli_parser.parse_args()

    return arguments


def _process(candidates: List[str], styles: Sequence[Style]) -> List[Issue]:
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


def _configure(project_file: Path = None) -> Configuration:
    configuration = Configuration()
    # TODO /etc/fab.ini
    # TODO ~/.fab.ini - Path.home() / '.fab.ini'
    if project_file is not None:
        configuration = ConfigurationFile(project_file, configuration)
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
    if arguments.style is not None:
        for name in arguments.style:
            styles.append(determine_style(configuration, name))
    else:
        styles.append(determine_style(configuration))

    # Pipelines loaded from configuration file
    #
    for extension, language, preprocessors in configuration.get_file_pipes():
        SourceFactory.add_extension(extension, language, *preprocessors)
    #
    # Pipelines from command line.
    #
    for mapping in arguments.map_extension:
        extension, language, preprocessors \
            = Configuration.parse_pipe_description(mapping)
        SourceFactory.add_extension(extension, language, *preprocessors)

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
