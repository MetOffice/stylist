#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Issues found in the source.
"""
from pathlib import Path
from typing import Optional


class Issue:
    """
    Holds details pertaining to an issue with the source.
    """
    def __init__(self,
                 description: str,
                 line: Optional[int] = None,
                 filename: Optional[Path] = None) -> None:
        """
        :param description: Free-format string describing the issue.
        :param line: Line number where issue found.
        :param filename: File in which issue found.
        """
        self._filename = filename
        self._line = line
        self._description = description

    def __str__(self) -> str:
        string = ''
        if self._filename:
            string += f'{str(self._filename)}: '
        if self._line:
            string += f'{self._line}: '
        string += f'{self._description}'
        return string.format(filename=self._filename,
                             line=self._line,
                             description=self._description)

    @property
    def filename(self) -> Optional[Path]:
        """
        Filename associated with this issue.
        """
        return self._filename

    @property
    def line(self) -> Optional[int]:
        """
        Line number associated with this issue.
        """
        return self._line

    @property
    def description(self) -> str:
        """
        Description of this issue.
        """
        return self._description

    def set_filename(self, filename: Path) -> None:
        """
        Associates a filename with this issue.
        """
        self._filename = filename
