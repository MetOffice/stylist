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
from typing import Dict, List, Mapping, Sequence, Set, Union

from stylist import StylistException


class Configuration(ABC):
    # Pycharm is confused by referring to the class you are defining. mypy is
    # fine with it.
    #
    def __init__(self,
                 parameters: Mapping[str,
                                     Mapping[str, str]],
                 defaults: 'Configuration' = None):
        self._defaults = defaults
        self._parameters = parameters

    _STYLE_PREFIX = 'style.'

    def available_styles(self) -> Sequence[str]:
        """
        Gets a list of all available styles.
        """
        styles: Set[str] = set()
        if self._defaults is not None:
            styles.update(self._defaults.available_styles())

        for section in self._parameters.keys():
            if section.startswith(self._STYLE_PREFIX):
                styles.add(section[len(self._STYLE_PREFIX):])

        return sorted(styles)

    def get_style(self, name: str) -> Sequence[str]:
        """
        Gets the rules associated with the provided style name.
        """
        key = self._STYLE_PREFIX + name
        if key in self._parameters:
            rules = self._parameters[key]['rules']
            if len(rules.strip()) == 0:
                raise StylistException(f"Style {key} contains no rules")
            else:
                return rules.split(',')
        else:  # key not in self._parameters
            if self._defaults is not None:
                return self._defaults.get_style(name)
            else:
                raise KeyError(f"Style '{key}' not found in configuration")


class ConfigurationFile(Configuration):
    """
    Configuration parameters read from a Windows .ini format file.
    """
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
        parameters: Dict[str, Dict[str, str]] = {}
        for section in parser.sections():
            parameters[section] = {}
            for key, value in parser.items(section):
                parameters[section][key] = value
        super().__init__(parameters, defaults)
