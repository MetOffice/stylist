#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Manages source code in various flavours.
'''
from __future__ import absolute_import, division, print_function

from abc import ABCMeta, abstractmethod
import re
import os.path
from six import add_metaclass

import fparser.common.readfortran as readfortran
import fparser.two.Fortran2003
from fparser.two.parser import ParserFactory
from fparser.two.utils import FparserException


@add_metaclass(ABCMeta)
class SourceText(object):
    # pylint: disable=too-few-public-methods
    '''
    Handles source code at the text level. Makes use of the decorator pattern
    to perform text level preprocessing.
    '''
    @abstractmethod
    def get_text(self):
        '''
        Gets the source file as a string.
        '''
        raise NotImplementedError()


class SourceFileReader(SourceText):
    # pylint: disable=too-few-public-methods
    '''
    Reads source from a file.
    '''
    def __init__(self, sourceFile):
        '''
        Constructor.
        Accepts either a filename or file-like object.
        '''
        if isinstance(sourceFile, str):
            with open(sourceFile, 'rt') as handle:
                self._cache = handle.read()
        else:
            self._cache = sourceFile.read()

    def get_text(self):
        return self._cache


class SourceStringReader(SourceText):
    # pylint: disable=too-few-public-methods
    '''
    Reads source from a string.
    '''
    def __init__(self, source_string):
        '''
        Constructor.
        '''
        self._source_string = source_string

    def get_text(self):
        return self._source_string


@add_metaclass(ABCMeta)
class TextProcessor(SourceText):
    # pylint: disable=too-few-public-methods, abstract-method
    '''
    Preprocessor decorators inherit from this.

    @param source The SourceText object which this object decorates.
    '''
    def __init__(self, source):
        self._source = source


class CPreProcessor(TextProcessor):
    # pylint: disable=too-few-public-methods
    '''
    Strips out preprocessor directives.

    It is assumed that you want to syntax check all the Source so all
    conditional directives such as '#ifdef' are stripped out.

    TODO: Currently all other directives are stripped out as well. This means
          that macros used to inject source are not likely to parse.
    '''
    _CONDITIONAL_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#if(def|\s+)*)$',
                                                re.MULTILINE)
    _OTHER_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#.*)$', re.MULTILINE)

    def get_text(self):
        '''
        Strips preprocessor directives from the text.
        '''
        text = self._source.get_text()
        text = self._CONDITIONAL_DIRECTIVE_PATTERN.sub(r'\1// \2', text)
        text = self._OTHER_DIRECTIVE_PATTERN.sub(r'\1// \2', text)
        return text


class FortranPreProcessor(TextProcessor):
    # pylint: disable=too-few-public-methods
    '''
    Strips out preprocessor directives.

    It is assumed that you want to syntax check all the Source so all
    conditional directives such as '#ifdef' are stripped out.

    TODO: Currently all other directives are stripped out as well. This means
          that macros used to inject source are not likely to parse.
    '''
    _CONDITIONAL_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#if(def|\s+)*)$',
                                                re.MULTILINE)
    _OTHER_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#.*)$', re.MULTILINE)

    def get_text(self):
        '''
        Strips preprocessor directives from the text.
        '''
        text = self._source.get_text()
        text = self._CONDITIONAL_DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        text = self._OTHER_DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        return text


class PFUnitProcessor(TextProcessor):
    # pylint: disable=too-few-public-methods
    '''
    Strips out pFUnit directives.
    '''
    _DIRECTIVE_PATTERN = re.compile(r'^(\s*)(@\w+.*)$', re.MULTILINE)

    def get_text(self):
        '''
        Strips processor directives from the text.
        '''
        text = self._source.get_text()
        text = self._DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        return text


@add_metaclass(ABCMeta)
class SourceTree(object):
    '''
    Abstract parent of all actual language source files.
    '''
    def __init__(self, text):
        if not isinstance(text, SourceText):
            raise Exception('text argument must derive from SourceText.')

        self._text = text
        self._tree = None
        self._tree_error = 'Not parsed yet'

    @abstractmethod
    def get_tree(self):
        '''
        Gets a parse-tree representation of the source file.
        '''
        raise NotImplementedError()

    @abstractmethod
    def get_tree_error(self):
        '''
        Gets any errors raised while building the parse tree.
        '''
        raise NotImplementedError()

    def get_text(self):
        '''
        Gets the original source text.
        '''
        return self._text.get_text()


class FortranSource(SourceTree):
    '''
    Holds a Fortran source file as both a text block and parse tree.
    '''
    def get_tree(self):
        if not self._tree:
            # We don't use the tree directly. Instead we let all the decorators
            # have a go first.
            reader = readfortran.FortranStringReader(self._text.get_text(),
                                                     ignore_comments=False)
            fortran_parser = ParserFactory().create(std='f2008')
            try:
                self._tree = fortran_parser(reader)
                self._tree_error = None
            except FparserException as ex:
                self._tree = None
                self._tree_error = str(ex)
        return self._tree

    def get_tree_error(self):
        return self._tree_error

    def get_first_statement(self, root=None):
        '''
        Gets the first "statement" part of the syntax tree or part thereof.
        '''
        if not root:
            root = self._tree.content

        root = [root]

        while root:
            candidate = root.pop(0)
            if isinstance(candidate, fparser.two.Fortran2003.StmtBase):
                return candidate

            if isinstance(candidate, fparser.two.Fortran2003.BlockBase):
                root.extend(candidate.content)
            elif isinstance(candidate, fparser.two.Fortran2003.SequenceBase):
                root.extend(candidate.items)
            elif isinstance(candidate, fparser.two.Fortran2003.Comment):
                pass
            else:
                message = 'Unexpected candidate type: {0}'
                raise Exception(message.format(candidate.__class__.__name__))
        return None

    def path(self, path, root=None):
        # pylint: disable=too-many-branches
        '''
        Returns the tree node described by the given path. The path may be
        presented as either a list of node name strings or as a '/' delimited
        string of node names.

        If the path is not found in the tree, returns an empty list.
        '''
        if isinstance(path, str):
            path = path.split('/')
        else:
            path = list(path)

        found = []
        if root:
            next_candidates = root
        else:
            next_candidates = list(self.get_tree().content)

        while path:
            node_name = path.pop(0)
            # pylint: disable=eval-used
            node_class = eval('fparser.two.Fortran2003.' + node_name)

            candidates = next_candidates
            next_candidates = []
            while candidates:
                candidate = candidates.pop(0)
                candidate_name = candidate.__class__.__name__
                node_subclasses = node_class.subclass_names
                # Only allow comments to be considered if we are looking for
                # a comment.
                if not isinstance(node_class, fparser.two.Fortran2003.Comment):
                    if 'Comment' in node_subclasses:
                        node_subclasses.remove('Comment')

                if self._ast_match(candidate, node_class):
                    if not path:  # Bottom of the path
                        found.append(candidate)

                    if isinstance(candidate,
                                  fparser.two.Fortran2003.BlockBase):
                        next_candidates.extend(candidate.content)
                    elif isinstance(candidate,
                                    fparser.two.Fortran2003.SequenceBase):
                        next_candidates.extend(candidate.items)
                    elif isinstance(candidate,
                                    fparser.two.Fortran2003.StmtBase):
                        pass
                    elif isinstance(candidate,
                                    fparser.two.Fortran2003.Comment):
                        pass
                    else:
                        message = 'Unexpected candidate type: {0}'
                        raise Exception(message.format(candidate_name))
        return found

    def find_all(self, find_node, root=None):
        '''
        Returns a generator which loops over all instances if the specified
        parse element below the root.

        The search descends the tree but that descent is terminated by a match.
        '''
        if root:
            candidates = [root]
        else:
            candidates = list(self.get_tree().content)

        while candidates:
            candidate = candidates.pop(0)
            if self._ast_match(candidate, find_node):
                yield candidate
            else:  # If we found a thing we don't descend into it
                if isinstance(candidate, fparser.two.Fortran2003.BlockBase):
                    candidates.extend(candidate.content)
                elif isinstance(candidate,
                                fparser.two.Fortran2003.SequenceBase):
                    candidates.extend(candidate.items)
                else:
                    pass

    @staticmethod
    def _ast_match(candidate, saught_class):
        if candidate.__class__.__name__ == saught_class.__name__:
            return True

        considering = [saught_class]
        for consideration in considering:
            if candidate.__class__.__name__ == consideration.__name__:
                return True
            # pylint: disable=eval-used
            considering.extend([eval('fparser.two.Fortran2003.' + name)
                                for name in consideration.subclass_names])

    @staticmethod
    def print_tree(children, indent=0):
        '''
        Dumps a textual representation of the tree to standard out.
        Intended for debug use.
        '''
        for child in children:
            print(' ' * indent + child.__class__.__name__)
            if isinstance(child, fparser.two.Fortran2003.BlockBase):
                FortranSource.print_tree(child.content, indent+1)
            elif isinstance(child, fparser.two.Fortran2003.SequenceBase):
                FortranSource.print_tree(child.items, indent+1)


class CSource(SourceTree):
    '''
    Holds a C/C++ source file as both a text block and parse tree.
    '''
    def get_tree(self):
        raise NotImplementedError('C/C++ source is not supported yet.')

    def get_tree_error(self):
        raise NotImplementedError('C/C++ source is not supported yet.')


class _SourceChain(object):
    # pylint: disable=too-few-public-methods
    '''
    Holds the chain of objects needed to understand a particular file
    extension.
    '''
    def __init__(self, extension, parser, *preprocessors):
        if extension[0] == '.':
            extension = extension[1:]
        self.extension = extension

        if not issubclass(parser, SourceTree):
            message = 'Object "{0}" must inherit SourceTree to be a parser.'
            raise Exception(message.format(parser.__class__.__name__))
        self.parser = parser

        for candidate in preprocessors:
            if not issubclass(candidate, SourceText):
                message = 'Object "{0}" must inherit SourceText' \
                          + ' to be a preprocessor'
                raise Exception(message.format(candidate.__class__.__name__))
        self.preprocessors = preprocessors


class SourceFactory(object):
    '''
    Manaages the handling of source file. Knows what chains of objects are
    needed to each file extension.
    '''
    # It is hard to lay down hard and fast rules about what should go in the
    # _extension_map list. Languages standards do not generally specify an
    # extension since it is an OS level concept.
    #
    # The default list should be kept short and the two goals should be
    # "correctness" and "commodity".
    #
    # Correctness means not including a slew of extensions just because they
    # happen to be used. Stick to ones which are "correct" in that they are
    # well thought out.
    #
    # For instance it is not uncommon for people to use all sorts of extensions
    # for Fortran which encodes the version of the language they are using.
    # This is a poor idea as it leads to a proliferation of extension for no
    # obvious gain. What's more a file with a ".f03" extension may be coded
    # using only Fortran 95 features.
    #
    # Instead we follow the convention that ".f90" means "free format" source
    # while ".f" continues to mean "fixed format".
    #
    # On the other hand commonality means including the most commonly used
    # extensions. That is why both ".cc" and ".cpp" are listed for C++ source.
    #
    # If your particular application needs to support some odd-ball extensions
    # then it can use the add_extension() call.
    #
    _extension_map = {'f90': _SourceChain('f90', FortranSource),
                      'F90': _SourceChain('F90',
                                          FortranSource, FortranPreProcessor),
                      'f': _SourceChain('f', FortranSource),
                      'F': _SourceChain('F',
                                        FortranSource, FortranPreProcessor),
                      'c': _SourceChain('c', CSource, CPreProcessor),
                      'h': _SourceChain('h', CSource, CPreProcessor),
                      'cc': _SourceChain('cc', CSource, CPreProcessor),
                      'cpp': _SourceChain('cpp', CSource, CPreProcessor)}

    @classmethod
    def add_extension(cls, extension, source, *preprocessors):
        '''
        Adds a mapping between source file extension and source handling
        classes.

        extension: str() File extension.
        source: class(LanguageSource) Source handler class.
        *preprocessors: class(SourceProcessor) Preprocessors to apply.
        '''
        if extension in cls._extension_map:
            raise Exception('Extension "{}" already mapped to a handler'
                            .format(extension))

        cls._extension_map[extension] = _SourceChain(extension,
                                                     source,
                                                     *preprocessors)

    @classmethod
    def get_extensions(cls):
        '''
        Gets the list of file extensions recognised by the read_file() method.
        '''
        return cls._extension_map.keys()

    @classmethod
    def read_file(cls, source_file):
        '''
        Creates a Source object from a file.

        The file extension is used to determine the source type so this will
        not work on "files" which do not have filenames.
        '''
        if isinstance(source_file, str):
            filename = source_file
        else:
            filename = source_file.name

        ext = os.path.splitext(filename)[1][1:]
        if ext not in cls._extension_map:
            raise Exception('Source file extension "{0}" not in handler map'
                            .format(ext))

        chain = cls._extension_map[ext]
        reader = SourceFileReader(source_file)
        # Decorate reader
        for handler_class in chain.preprocessors:
            reader = handler_class(reader)

        return chain.parser(reader)
