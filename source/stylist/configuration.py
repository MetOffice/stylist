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
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Dict, List, Tuple, Type

from stylist import StylistException
from stylist.source import (CPreProcessor,
                            CSource,
                            FilePipe,
                            FortranPreProcessor,
                            FortranSource,
                            PFUnitProcessor,
                            PlainText,
                            SourceTree,
                            TextProcessor)
from stylist.style import Style


class Configuration:
    def __init__(self) -> None:
        self._pipes: Dict[str, FilePipe] = {}
        self._styles: Dict[str, Style] = {}

    def add_pipe(self, extension: str, pipe: FilePipe):
        self._pipes[extension] = pipe

    def add_style(self, name: str, style: Style):
        self._styles[name] = style

    @property
    def file_pipes(self) -> Dict[str, FilePipe]:
        return self._pipes

    @property
    def styles(self) -> Dict[str, Style]:
        return self._styles


def load_configuration(config_file: Path) -> Configuration:
    spec = spec_from_file_location('configuration_file', config_file)
    if spec is None:
        message = f"Unable to find configuration file: {config_file}"
        raise StylistException(message)
    module = module_from_spec(spec)
    if spec.loader is None:
        message = f"Unable to find loader for file: {config_file}"
        raise StylistException(message)
    spec.loader.exec_module(module)
    configuration = Configuration()
    for name, var in module.__dict__.items():
        if isinstance(var, FilePipe):
            configuration.add_pipe(name, var)
        elif isinstance(var, Style):
            configuration.add_style(name, var)

    return configuration


class ConfigTools:
    _LANGUAGE_MAP: Dict[str, Type[SourceTree]] \
        = {'c': CSource,
           'cxx': CSource,
           'fortran': FortranSource,
           'text': PlainText}

    @classmethod
    def language_keys(cls) -> List[str]:
        return list(cls._LANGUAGE_MAP.keys())

    @classmethod
    def language(cls, key: str) -> Type[SourceTree]:
        return cls._LANGUAGE_MAP[key]

    _PREPROCESSOR_MAP: Dict[str, Type[TextProcessor]] \
        = {'cpp': CPreProcessor,
           'fpp': FortranPreProcessor,
           'pfp': PFUnitProcessor}

    @classmethod
    def preprocessor_keys(cls) -> List[str]:
        return list(cls._PREPROCESSOR_MAP.keys())

    @classmethod
    def preprocessor(cls, key: str) -> Type[TextProcessor]:
        return cls._PREPROCESSOR_MAP[key]

    @classmethod
    def parse_pipe_description(cls, string: str) -> Tuple[str, FilePipe]:
        """
        Converts a pipeline description into classes.

        :param string: Colon-separated list of extension and pipeline stages.
        """
        if not string:
            raise StylistException("Empty extension pipe description")

        bits = string.split(':', 2)
        extension = bits[0]
        lang_object = cls._LANGUAGE_MAP[bits[1].lower()]
        preproc_objects: List[Type[TextProcessor]]
        if len(bits) > 2:
            preproc_objects = [cls._PREPROCESSOR_MAP[ident.lower()]
                               for ident in bits[2].split(':')]
        else:
            preproc_objects = []
        return extension, FilePipe(lang_object, *preproc_objects)
