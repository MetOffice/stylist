#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Tool for checking code style.
'''

from __future__ import absolute_import, division, print_function

import argparse
import logging
import os.path
import sys

from stylist.engine import CheckEngine
from stylist.source import CPreProcessor, CSource, FortranPreProcessor, \
                           FortranSource, PFUnitProcessor, \
                           SourceFactory
from stylist.style import LFRicStyle


def parse_cli():
    '''
    Parse the command line. Returns a dictionary of arguments.
    '''
    description = 'Perform various code style checks on source code.'
    cli_parser = argparse.ArgumentParser(add_help=False,
                                         description=description)
    cli_parser.add_argument('-help', '-h', '--help', action='help')
    cli_parser.add_argument('-verbose', '-v', action="store_true",
                            help='Produce a running commentary on progress')
    message = 'Add a mapping between file extension and language'
    cli_parser.add_argument('-map-extension',
                            metavar='EXTENSION:LANGUAGE[:PREPROCESSOR]',
                            dest='map_extension',
                            default=[],
                            action='append',
                            help=message)
    cli_parser.add_argument('source', metavar='FILE', nargs='+',
                            help='Filename of source file or directory')
    return cli_parser.parse_args()


_LANGUAGE_MAP = {'c': CSource,
                 'cxx': CSource,
                 'fortran': FortranSource}
_PREPROCESSOR_MAP = {'cpp': CPreProcessor,
                     'fpp': FortranPreProcessor,
                     'pfp': PFUnitProcessor}


def _add_extensions(additional_extensions):
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

    for mapping in additional_extensions:
        extension, language, preprocessors = mapping.split(':', 2)
        preprocessors = preprocessors.split(':')
        preproc_objects = [_PREPROCESSOR_MAP[ident.lower()]
                           for ident in preprocessors]
        SourceFactory.add_extension(extension.lower(),
                                    _LANGUAGE_MAP[language.lower()],
                                    *preproc_objects)


def process(arguments):
    '''
    Examines files for style compliance.

    Any directories specified will be descended looking for files to examine.
    '''
    logger = logging.getLogger('stylist')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    if arguments.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    _add_extensions(arguments.map_extension)

    styles = [LFRicStyle()]
    engine = CheckEngine(styles)

    hot_extensions = SourceFactory.get_extensions()

    candidates = arguments.source
    issues = []
    while candidates:
        filename = candidates.pop(0)
        if os.path.isdir(filename):
            for leaf in os.listdir(filename):
                leaf_filename = os.path.join(filename, leaf)
                _, extension = os.path.splitext(leaf_filename)
                if extension[1:] in hot_extensions \
                   or os.path.isdir(leaf_filename):
                    candidates.append(leaf_filename)
        else:  # Is a file
            issues.extend(engine.check(filename))

    for issue in issues:
        print(str(issue), file=sys.stderr)
    if (len(issues) > 0) or arguments.verbose:
        print('Found {number} issues'.format(number=len(issues)))

    if issues:
        sys.exit(1)


def main():
    '''Main entry point.'''
    return process(parse_cli())


if __name__ == '__main__':
    main()
