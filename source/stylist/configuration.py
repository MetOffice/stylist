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
import re
from typing import Dict, Mapping, Sequence, Set, Tuple, Type, Pattern

from stylist import StylistException
from stylist.source import (CPreProcessor,
                            CSource,
                            FortranPreProcessor,
                            FortranSource,
                            PFUnitProcessor,
                            PlainText,
                            SourceTree,
                            TextProcessor)


class Configuration(ABC):
    # Pycharm is confused by referring to the class you are defining. mypy is
    # fine with it.
    #
    def __init__(self,
                 parameters: Mapping[str,
                                     Mapping[str, str]] = None,
                 defaults: 'Configuration' = None):
        self._defaults = defaults
        if parameters is not None:
            self._parameters = parameters
        else:
            self._parameters = {}

    _LANGUAGE_MAP: Mapping[str, Type[SourceTree]] \
        = {'c': CSource,
           'cxx': CSource,
           'fortran': FortranSource,
           'text': PlainText}

    @classmethod
    def language_tags(cls):
        return cls._LANGUAGE_MAP.keys()

    @classmethod
    def language_lookup(cls, key: str) -> Type[SourceTree]:
        return cls._LANGUAGE_MAP[key]

    _PREPROCESSOR_MAP: Mapping[str, Type[TextProcessor]] \
        = {'cpp': CPreProcessor,
           'fpp': FortranPreProcessor,
           'pfp': PFUnitProcessor}

    @classmethod
    def preprocessor_tags(cls):
        return cls._PREPROCESSOR_MAP.keys()

    @classmethod
    def preprocessor_lookup(cls, key: str) -> Type[TextProcessor]:
        return cls._PREPROCESSOR_MAP[key]

    @classmethod
    def parse_pipe_description(cls, string: str) \
        -> Tuple[str,
                 Type[SourceTree],
                 Sequence[Type[TextProcessor]]]:
        if not string:
            raise StylistException("Empty extension pipe description")

        bits = string.split(':', 2)
        extension = bits[0]
        lang_object = cls._LANGUAGE_MAP[bits[1].lower()]
        if len(bits) > 2:
            preproc_objects = [cls._PREPROCESSOR_MAP[ident.lower()]
                               for ident in bits[2].split(':')]
        else:
            preproc_objects = []
        return extension, lang_object, preproc_objects

    def get_file_pipes(self) -> Sequence[Tuple[str,
                                               Type[SourceTree],
                                               Sequence[Type[TextProcessor]]]]:
        """
        Enumerates the extension handling pipelines.
        """
        result = []
        section = self._parameters.get('file-pipe')
        if section is not None:
            for extension in section:
                descr = f'{extension}:{section[extension]}'
                result.append(self.parse_pipe_description(descr))
        return result

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

    # This rule will not handle brackets appearing within the argument list.
    #
    _RULE_PATTERN: Pattern[str] \
        = re.compile(r'(?:^|,)\s*(.+?(?:\(.*?\))?(?=,|$))')

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
                return self._RULE_PATTERN.findall(rules)
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
