#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2018 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Checks source code management classes.
'''
from __future__ import absolute_import, division, print_function

import os.path
import shutil
import tempfile

import fparser.two.Fortran2003
import pytest

from stylist.source import CPreProcessor, CSource, \
                           FortranPreProcessor, FortranSource, \
                           PFUnitProcessor, \
                           SourceFactory, \
                           SourceFileReader, SourceStringReader, \
                           SourceText, SourceTree, \
                           _SourceChain


class TestSourceText(object):
    '''
    Checks the TextSource heirarchy.
    '''
    def testSourceStringReader(self):
        # pylint: disable=no-self-use
        '''
        Checks that the text can be retrieved from a string reader.
        '''
        text = 'Peek-a-boo!\nI see you.\n'
        expected = text
        unit_under_test = SourceStringReader(text)
        assert unit_under_test.get_text() == expected

    def testSourceFileReaderFilename(self, tmpdir):
        # pylint: disable=no-self-use
        '''
        Checks that the text can be retrieved from a named file.
        '''
        text = 'Here, here in this file.\nAll things may be found.\n'
        filename = tmpdir / 'test.txt'
        filename.write(text)

        unit_under_test = SourceFileReader(filename)
        assert unit_under_test.get_text() == text

    def testSourceFileReaderFile(self, tmpdir):
        # pylint: disable=no-self-use
        '''
        Checks that the text can be retrieved from a file object.
        '''
        text = 'Here, here in this file.\nAll things may be found.\n'
        filename = tmpdir.join('test.txt')
        filename.write(text)

        with filename.open('rt') as handle:
            unit_under_test = SourceFileReader(handle)
            assert unit_under_test.get_text() == text


class TestPPFortranSource(object):
    def test_preprocessed_fortran_source(self):
        # pylint: disable=no-self-use
        source = '''! Some things happen, others don't
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
'''
        expected = '''! Some things happen, others don't
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
'''
        reader = SourceStringReader(source)
        unit_under_test = FortranPreProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestPPpFUnitSource(object):
    def test_preprocessed_pfunit_source(self):
        # pylint: disable=no-self-use
        source = '''! Test all the things
module test_mod
  use pFUnit
  implicit none
contains
  @test
  subroutine test_normal()
  end subroutine test_normal
end module test_mod
'''
        expected = '''! Test all the things
module test_mod
  use pFUnit
  implicit none
contains
  ! @test
  subroutine test_normal()
  end subroutine test_normal
end module test_mod
'''
        reader = SourceStringReader(source)
        unit_under_test = PFUnitProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestPPCSource(object):
    def test_preprocessed_c_source(self):
        # pylint: disable=no-self-use
        source = '''/* Some things happen, others don't */
#ifndef TEST_HEADER
#define TEST_HEADER

  #include <stdbool.h>

int normal(void);
#ifdef EXTRA
char *more(void);
#endif
#endif
'''
        expected = '''/* Some things happen, others don't */
// #ifndef TEST_HEADER
// #define TEST_HEADER

  // #include <stdbool.h>

int normal(void);
// #ifdef EXTRA
char *more(void);
// #endif
// #endif
'''
        reader = SourceStringReader(source)
        unit_under_test = CPreProcessor(reader)
        assert unit_under_test.get_text() == expected


class TestFortranSource(object):
    '''
    Checks the Fortran source class.
    '''
    def test_constructor(self):
        '''
        Checks that the source file is correctly parsed on construction.
        '''
        # pylint: disable=no-self-use
        inject = r'''! Test program
program test
  implicit none
  write(6, '("Hello ", A)') 'world'
end program test
'''
        reader = SourceStringReader(inject)
        unit_under_test = FortranSource(reader)
        assert unit_under_test.get_text() == inject

        expected_string = '''! Test program
PROGRAM test
  IMPLICIT NONE
  WRITE(6, FMT = '("Hello ", A)') 'world'
END PROGRAM test'''
        assert str(unit_under_test.get_tree()) == expected_string

    _SIMPLE_PROGRAM = r'''! Test program
                          program test
                            implicit none
                            write(6, '("Hello ", A)') 'world'
                          end program test
                       '''
    _BARE_SUBROUTINE = r'''subroutine testing
                           end subroutine testing'''
    _MULTI_PROC_MODULE = r'''! Initial comment
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
                          '''

    @pytest.fixture(scope="class",
                    params=([_SIMPLE_PROGRAM,
                             ['Program_Unit'],
                             ['Main_Program']],
                            [_BARE_SUBROUTINE,
                             ['Program_Unit'],
                             ['Subroutine_Subprogram']],
                            [_SIMPLE_PROGRAM,
                             ['Program_Unit', 'Specification_Part',
                              'Implicit_Part', 'Implicit_Stmt'],
                             ['Implicit_Stmt']]))
    def path_case(self, request):
        '''
        Generates a series of test cases for path searching a source file.
        '''
        # pylint: disable=no-self-use
        yield request.param

    def test_path_list(self, path_case):
        '''
        Checks that matching a path to the source works.
        '''
        # pylint: disable=no-self-use
        reader = SourceStringReader(path_case[0])
        unit_under_test = FortranSource(reader)
        result = unit_under_test.path(path_case[1])
        assert [obj.__class__.__name__ for obj in result] == path_case[2]

    def test_path_string(self, path_case):
        '''
        Checks that matching a path to the source works.
        '''
        # pylint: disable=no-self-use
        reader = SourceStringReader(path_case[0])
        unit_under_test = FortranSource(reader)
        result = unit_under_test.path('/'.join(path_case[1]))
        assert [obj.__class__.__name__ for obj in result] == path_case[2]

    def test_find_all(self):
        '''
        Checks that finding all occurrences of a source part works.
        '''
        reader = SourceStringReader(self._MULTI_PROC_MODULE)
        unit_under_test = FortranSource(reader)
        wanted = fparser.two.Fortran2003.Module_Subprogram
        result = unit_under_test.find_all(wanted)
        assert str(result.next().content[0].items[1]) == 'one'
        assert str(result.next().content[0].items[1]) == 'two'
        with pytest.raises(StopIteration):
            result.next()


class TestCSource(object):
    # pylint: disable=too-few-public-methods
    '''
    Checks the C/C++ source class.
    '''
    def test_constructor(self):
        '''
        Checks that the source file is correctly parsed on construction.
        '''
        pass


class TestSourceChain(object):
    '''
    Checks the description of a chain of source processing.
    '''
    class ReaderHarness(SourceText):
        def get_text(self):
            pass

    @pytest.fixture(scope="module", params=['.dot', 'nodot'])
    def chain_extension(self, request):
        '''
        Generates a file extension with and without leading dot.
        '''
        return request.param

    class LanguageHarness(SourceTree):
        def __init__(self):
            reader = TestSourceChain.ReaderHarness()
            super(TestSourceChain.LanguageHarness, self).__init__(reader)

        def get_tree(self):
            pass

        def get_tree_error(self):
            pass

    class TextHarness(SourceText):
        pass

    @pytest.fixture(scope="module", params=[(),
                                            tuple([TextHarness]),
                                            (TextHarness, TextHarness)])
    def chain_text(self, request):
        '''
        Generates a tuple of text source classes.
        '''
        return request.param

    def test_constructor(self, chain_extension, chain_text):
        unit_under_test = _SourceChain(chain_extension,
                                       TestSourceChain.LanguageHarness,
                                       *chain_text)
        assert unit_under_test.extension == chain_extension.strip('.')
        assert unit_under_test.parser == TestSourceChain.LanguageHarness
        assert unit_under_test.preprocessors == chain_text


class TestFactory(object):
    '''
    Checks the factory is able to manufacture source.
    '''
    @pytest.fixture(scope="module",
                    params=['f', 'F', 'f90', 'F90'])
    def fortran_extension(self, request):
        '''
        Generates a series of Fortran source file extensions.
        '''
        # pylint: disable=no-self-use
        return request.param

    @pytest.fixture(scope="module",
                    params=['c', 'cc', 'cpp', 'h'])
    def cxx_extension(self, request):
        '''
        Generates a series of C and C++ source file extensions
        '''
        # pylint: disable=no-self-use
        return request.param

    def test_read_fortran_files(self, tmpdir, fortran_extension):
        '''
        Checks that read_file() can correctly identify Fortran source files and
        produce FortranSource objects from them.
        '''
        # pylint: disable=no-self-use
        source = '''module test_mod
  implicit none
  private
contains
end module test_mod
'''
        expected = '''MODULE test_mod
  IMPLICIT NONE
  PRIVATE
  CONTAINS
END MODULE test_mod'''
        source_filename = tmpdir.join('test.' + fortran_extension)
        source_filename.write(source)
        result = SourceFactory.read_file(str(source_filename))
        assert isinstance(result, FortranSource)
        assert str(result.get_tree()) == expected

    def test_read_c_files(self, tmpdir, cxx_extension):
        '''
        Checks that read_file() can correctly identify a C source files and
        produce CSource objects from them.
        '''
        # pylint: disable=no-self-use
        source = r'''#include <stdio>
int main(int argc, char **argv) {
    printf("Hello %s", "world")
    return 0
}
'''
        source_filename = tmpdir.join('test.' + cxx_extension)
        source_filename.write(source)
        tree = SourceFactory.read_file(str(source_filename))
        assert isinstance(tree, CSource)
        with pytest.raises(NotImplementedError):
            _ = tree.get_tree()

    def test_add_extension(self, tmpdir):
        '''
        Checks that adding an extension allows read_file() to process a file
        with that new extension.
        '''
        # pylint: disable=no-self-use
        source = '''module test_mod
  implicit none
  private
contains
end module test_mod
'''
        expected = '''MODULE test_mod
  IMPLICIT NONE
  PRIVATE
  CONTAINS
END MODULE test_mod'''
        source_filename = tmpdir.join('test.x90')
        source_filename.write(source)
        with pytest.raises(Exception):
            result = SourceFactory.read_file(str(source_filename))
        SourceFactory.add_extension('x90', FortranSource)
        result = SourceFactory.read_file(str(source_filename))
        assert isinstance(result, FortranSource)
        assert str(result.get_tree()) == expected
