#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2020 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Handles configuration parameters coming from various potential sources.

Configuration may be defined by software or read from a Windows .ini file.
"""
from abc import ABC
from configparser import ConfigParser, MissingSectionHeaderError
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Set, Sequence, Union


class Configuration(ABC):
    # Pycharm is confused by referring to the class you are defining. mypy is
    # fine with it.
    #
    def __init__(self,
                 parameters: Mapping[str, Mapping[str, Union[str,
                                                             int,
                                                             List[str]]]],
                 defaults: 'Configuration' = None):
        self._defaults = defaults
        self._parameters = parameters

    def section_names(self, prefix=None) -> Sequence[str]:
        """
        Gets a tuple of all section names.
        """
        candidates: Set[str] = set(self._parameters.keys())
        if self._defaults is not None:
            candidates = candidates.union(self._defaults.section_names())
        names: Iterable[str]
        if prefix is not None:
            names = [name for name in candidates
                     if name.startswith(prefix)]
        else:  # prefix is None
            names = candidates
        return list(sorted(names))

    def section(self, name: str) -> Mapping[str, Union[str, int, List[str]]]:
        """
        Gets a mapping of all key/value pairs from a section.
        """
        parameters: Dict[str, Union[str, int, List[str]]]
        if self._defaults is not None:
            parameters = dict(self._defaults.section(name))
        else:
            parameters = {}
        try:
            parameters.update(self._parameters[name])
        except KeyError:
            pass  # Not an error
        return parameters


class ConfigurationFile(Configuration):
    """
    Configuration parameters read from a Windows .ini format file.
    """
    _LISTS = ['rules']

    def __init__(self,
                 filename: Path,
                 defaults: Configuration = None) -> None:
        """
        Builds a configuration object from a filename.
        """
        parser = ConfigParser()
        try:
            with filename.open('rt') as handle:
                parser.read_file(handle)
        except MissingSectionHeaderError:
            pass  # It is not an error to have an empty configuration file.
        parameters: Dict[str, Dict[str, Union[str, List[str]]]] = {}
        for section in parser.sections():
            parameters[section] = {}
            for key, value in parser.items(section):
                if key in self._LISTS:
                    parameters[section][key] = value.split(',')
                else:
                    parameters[section][key] = value
        super().__init__(parameters, defaults)
