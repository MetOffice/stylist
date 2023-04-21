#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Checks source code management classes.
"""
from pathlib import Path
from typing import List, Tuple, Type

import fparser.two.Fortran2003  # type: ignore
import pytest  # type: ignore

from stylist.source import (CPreProcessor, CSource,
                            FortranPreProcessor, FortranSource,
                            PFUnitProcessor,
                            SourceFactory,
                            SourceFileReader, SourceStringReader,
                            SourceText, SourceTree,
                            TextProcessor,
                            FilePipe)


class TestSourceText:
    """
    Checks the TextSource hierarchy.
    """
    def test_source_string_reader(self) -> None:
        """
        Checks that the text can be retrieved from a string reader.
        """
        text = 'Peek-a-boo!\nI see you.\n'
        expected = text
        unit_under_test = SourceStringReader(text)
        assert unit_under_test.get_text() == expected

    def test_source_file_reader_filename(self, tmp_path: Path) -> None:
        """
        Checks that the text can be retrieved from a named file.
        """
        text = 'Here, here in this file.\nAll things may be found.\n'
        filename = tmp_path / 'test.txt'
        filename.write_text(text)

        unit_under_test = SourceFileReader(filename.open('r'))
        assert unit_under_test.get_text() == text

    def test_source_file_reader_file(self, tmp_path: Path) -> None:
        """
        Checks that the text can be retrieved from a file object.
        """
        text = 'Here, here in this file.\nAll things may be found.\n'
        filename = tmp_path / 'test.txt'
        filename.write_text(text)

        with filename.open('rt') as handle:
            unit_under_test = SourceFileReader(handle)
            assert unit_under_test.get_text() == text


class TestPPFortranSource:
    def test_name(self) -> None:
        assert FortranPreProcessor.get_name() == 'Fortran preprocessor'

    def test_preprocessed_fortran_source(self) -> None:
        source = """! Some things happen, others don't
module test_mod
#ifdef EXTRA
  use extra_mod, only: special
#endif
  implicit none
contains
  function normal()
  end function normal
  #ifdef EXTRA
  function more()
  end function more
  #endif EXTRA
end module test_mod
"""
        expected = """! Some things happen, others don't
module test_mod
! #ifdef EXTRA
  use extra_mod, only: special
! #endif
  implicit none
contains
  function normal()
  end function normal
  ! #ifdef EXTRA
  function more()
  end function more
  ! #endif EXTRA
end module test_mod
"""
        reader = SourceStringReader(source)
        unit_under_test = FortranPreProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestPPpFUnitSource:
    def test_name(self) -> None:
        assert PFUnitProcessor.get_name() == 'pFUnit preprocessor'

    def test_preprocessed_pfunit_source(self) -> None:
        source = """! Test all the things
module test_mod
  use pFUnit
  implicit none
contains
  @test
  subroutine test_normal()
  end subroutine test_normal
end module test_mod
"""
        expected = """! Test all the things
module test_mod
  use pFUnit
  implicit none
contains
  ! @test
  subroutine test_normal()
  end subroutine test_normal
end module test_mod
"""
        reader = SourceStringReader(source)
        unit_under_test = PFUnitProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestPPCSource:
    def test_name(self) -> None:
        assert CPreProcessor.get_name() == 'C preprocessor'

    def test_preprocessed_c_source(self) -> None:
        source = """/* Some things happen, others don't */
#ifndef TEST_HEADER
#define TEST_HEADER

  #include <stdbool.h>

int normal(void);
#ifdef EXTRA
char *more(void);
#endif
#endif
"""
        expected = """/* Some things happen, others don't */
// #ifndef TEST_HEADER
// #define TEST_HEADER

  // #include <stdbool.h>

int normal(void);
// #ifdef EXTRA
char *more(void);
// #endif
// #endif
"""
        reader = SourceStringReader(source)
        unit_under_test = CPreProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestFortranSource:
    """
    Checks the Fortran source class.
    """
    def test_name(self) -> None:
        assert FortranSource.get_name() == 'Fortran source'

    def test_constructor(self) -> None:
        """
        Checks that the source file is correctly parsed on construction.
        """
        inject = r"""! Test program
program test
  implicit none
  write(6, '("Hello ", A)') 'world'
end program test
"""
        reader = SourceStringReader(inject)
        unit_under_test = FortranSource(reader)
        assert unit_under_test.get_text() == inject

        expected_string = """! Test program
PROGRAM test
  IMPLICIT NONE
  WRITE(6, '("Hello ", A)') 'world'
END PROGRAM test"""
        assert str(unit_under_test.get_tree()) == expected_string

    _SIMPLE_PROGRAM = r"""! Test program
                          program test
                            implicit none
                            write(6, '("Hello ", A)') 'world'
                          end program test
                       """
    _BARE_SUBROUTINE = r"""subroutine testing
                           end subroutine testing"""
    _MULTI_PROC_MODULE = r"""! Initial comment
                             module multi
                               implicit none
                             contains
                               subroutine one()
                                 implicit none
                               end subroutine one
                               function two()
                                 implicit none
                                 integer :: two
                                 two = 2
                               end function two
                             end module multi
                          """

    @pytest.fixture(scope="class",
                    params=[(_SIMPLE_PROGRAM,
                             ['Program_Unit'],
                             ['Main_Program']),
                            (_BARE_SUBROUTINE,
                             ['Program_Unit'],
                             ['Subroutine_Subprogram']),
                            (_SIMPLE_PROGRAM,
                             ['Program_Unit', 'Specification_Part',
                              'Implicit_Part', 'Implicit_Stmt'],
                             ['Implicit_Stmt'])])
    def path_case(self, request):
        """
        Generates a series of test cases for path searching a source file.
        """
        return request.param

    def test_path_list(self, path_case: Tuple[str, List[str], List[str]]) \
            -> None:
        """
        Checks that matching a path to the source works.
        """
        reader = SourceStringReader(path_case[0])
        unit_under_test = FortranSource(reader)
        result = unit_under_test.path(path_case[1])
        assert [obj.__class__.__name__ for obj in result] == path_case[2]

    def test_path_string(self, path_case: Tuple[str, List[str], List[str]]) \
            -> None:
        """
        Checks that matching a path to the source works.
        """
        reader = SourceStringReader(path_case[0])
        unit_under_test = FortranSource(reader)
        result = unit_under_test.path('/'.join(path_case[1]))
        assert [obj.__class__.__name__ for obj in result] == path_case[2]

    def test_find_all(self) -> None:
        """
        Checks that finding all occurrences of a source part works.
        """
        reader = SourceStringReader(self._MULTI_PROC_MODULE)
        unit_under_test = FortranSource(reader)
        wanted = fparser.two.Fortran2003.Module_Subprogram
        result = unit_under_test.find_all(wanted)
        assert str(next(result).content[0].items[1]) == 'one'
        assert str(next(result).content[0].items[1]) == 'two'
        with pytest.raises(StopIteration):
            next(result)


class TestCSource:
    """
    Checks the C/C++ source class.
    """
    def test_name(self) -> None:
        assert CSource.get_name() == 'C source'

    def test_constructor(self) -> None:
        """
        Checks that the source file is correctly parsed on construction.
        """
        pass


class TestSourceChain:
    """
    Checks the description of a chain of source processing.
    """
    class ReaderHarness(SourceText):
        def get_text(self) -> str:
            return ''

    @pytest.fixture(scope="module", params=['.dot', 'nodot'])
    def chain_extension(self, request):
        """
        Generates a file extension with and without leading dot.
        """
        return request.param

    class LanguageHarness(SourceTree):
        def __init__(self) -> None:
            reader = TestSourceChain.ReaderHarness()
            super().__init__(reader)

        @staticmethod
        def get_name() -> str:
            return "language harness"

        def get_tree(self) -> None:
            pass

        def get_tree_error(self) -> None:
            pass

    class TextHarness(SourceText):
        def get_text(self) -> str:
            return "harness text"

        @staticmethod
        def get_name() -> str:
            return "text harness"

    class ProcessorHarness(TextProcessor):
        def get_text(self) -> str:
            return "processor text"

        @staticmethod
        def get_name() -> str:
            return "processor harness"

    @pytest.fixture(scope="module",
                    params=[[],
                            [ProcessorHarness],
                            [ProcessorHarness, ProcessorHarness]])
    def chain_text(self, request):
        """
        Generates a tuple of text source classes.
        """
        return request.param

    def test_constructor(self,
                         chain_extension: str,
                         chain_text: List[Type[ProcessorHarness]]) -> None:
        unit_under_test = FilePipe(TestSourceChain.LanguageHarness,
                                   *chain_text)
        assert unit_under_test.parser == TestSourceChain.LanguageHarness
        assert unit_under_test.preprocessors == tuple(chain_text)


class TestFactory:
    """
    Checks the factory is able to manufacture source.
    """
    @pytest.fixture(scope="module",
                    params=['f', 'F', 'f90', 'F90'])
    def fortran_extension(self, request):
        """
        Generates a series of Fortran source file extensions.
        """
        return request.param

    @pytest.fixture(scope="module",
                    params=['c', 'cc', 'cpp', 'h'])
    def cxx_extension(self, request):
        """
        Generates a series of C and C++ source file extensions
        """
        return request.param

    def test_read_fortran_files(self,
                                tmp_path: Path,
                                fortran_extension: str) -> None:
        """
        Checks that read_file() can correctly identify Fortran source files and
        produce FortranSource objects from them.
        """
        source = """module test_mod
  implicit none
  private
contains
end module test_mod
"""
        expected = """MODULE test_mod
  IMPLICIT NONE
  PRIVATE
  CONTAINS
END MODULE test_mod"""
        source_filename = tmp_path / f'test.{fortran_extension}'
        source_filename.write_text(source)
        result = SourceFactory.read_file(source_filename)
        assert isinstance(result, FortranSource)
        assert str(result.get_tree()) == expected

    def test_read_c_files(self, tmp_path: Path, cxx_extension: str) -> None:
        """
        Checks that read_file() can correctly identify a C source files and
        produce CSource objects from them.
        """
        source = r"""#include <stdio>
int main(int argc, char **argv) {
    printf("Hello %s", "world")
    return 0
}
"""
        source_filename = tmp_path / f'test.{cxx_extension}'
        source_filename.write_text(source)
        tree = SourceFactory.read_file(source_filename)
        assert isinstance(tree, CSource)
        with pytest.raises(NotImplementedError):
            _ = tree.get_tree()

    def test_add_extension(self, tmp_path: Path) -> None:
        """
        Checks that adding an extension allows read_file() to process a file
        with that new extension.
        """
        source = """module test_mod
  implicit none
  private
contains
end module test_mod
"""
        expected = """MODULE test_mod
  IMPLICIT NONE
  PRIVATE
  CONTAINS
END MODULE test_mod"""
        source_filename = tmp_path / 'test.x90'
        source_filename.write_text(source)
        with pytest.raises(Exception):
            result = SourceFactory.read_file(source_filename)
        SourceFactory.add_extension('x90', FilePipe(FortranSource))
        result = SourceFactory.read_file(source_filename)
        assert isinstance(result, FortranSource)
        assert str(result.get_tree()) == expected
