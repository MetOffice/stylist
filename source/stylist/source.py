#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Manages source code in various flavours.
"""
from abc import ABCMeta, abstractmethod
import re
import os.path
from typing import (Generator,
                    IO,
                    Iterable,
                    List,
                    Optional,
                    Type,
                    Union)

import fparser.common.readfortran as readfortran  # type: ignore
import fparser.two.Fortran2003 as Fortran2003  # type: ignore
from fparser.two.parser import ParserFactory  # type:ignore
from fparser.two.utils import FparserException  # type: ignore

from stylist import StylistException


class SourceText(object, metaclass=ABCMeta):
    """
    Handles source code at the text level. Makes use of the decorator pattern
    to perform text level preprocessing.
    """
    @abstractmethod
    def get_text(self) -> str:
        """
        Gets the source file as a string.
        """
        raise NotImplementedError()


class SourceFileReader(SourceText):
    """
    Reads source from a file.
    """
    def __init__(self, source_file: Union[IO[str], str]) -> None:
        """
        Constructor.
        Accepts either a filename or file-like object.
        """
        if isinstance(source_file, str):
            with open(source_file, 'rt') as handle:
                self._cache = handle.read()
        else:
            self._cache = source_file.read()

    def get_text(self) -> str:
        return self._cache


class SourceStringReader(SourceText):
    """
    Reads source from a string.
    """
    def __init__(self, source_string: str) -> None:
        """
        Constructor.
        """
        self._source_string = source_string

    def get_text(self) -> str:
        return self._source_string


class TextProcessor(SourceText, metaclass=ABCMeta):
    """
    Preprocessor decorators inherit from this. This is part of the decorator
    pattern.
    """
    def __init__(self, source: SourceText) -> None:
        """
        Constructs a preprocessor object which decorates a source of text.
        """
        self._source = source


class MetaCPreProcessor(ABCMeta):
    def __str__(self) -> str:
        return "C preprocessor"


class CPreProcessor(TextProcessor, metaclass=MetaCPreProcessor):
    """
    Strips out preprocessor directives.

    It is assumed that you want to syntax check all the Source so all
    conditional directives such as '#ifdef' are stripped out.

    TODO: Currently all other directives are stripped out as well. This means
          that macros used to inject source are not likely to parse.
    """
    _CONDITIONAL_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#if(def|\s+)*)$',
                                                re.MULTILINE)
    _OTHER_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#.*)$', re.MULTILINE)

    def get_text(self) -> str:
        """
        Strips preprocessor directives from the text.
        """
        text = self._source.get_text()
        text = self._CONDITIONAL_DIRECTIVE_PATTERN.sub(r'\1// \2', text)
        text = self._OTHER_DIRECTIVE_PATTERN.sub(r'\1// \2', text)
        return text


class MetaFortranPreProcessor(ABCMeta):
    def __str__(self) -> str:
        return "Fortran preprocessor"


class FortranPreProcessor(TextProcessor, metaclass=MetaFortranPreProcessor):
    """
    Strips out preprocessor directives.

    It is assumed that you want to syntax check all the Source so all
    conditional directives such as '#ifdef' are stripped out.

    TODO: Currently all other directives are stripped out as well. This means
          that macros used to inject source are not likely to parse.
    """
    _CONDITIONAL_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#if(def|\s+)*)$',
                                                re.MULTILINE)
    _OTHER_DIRECTIVE_PATTERN = re.compile(r'^(\s*)(#.*)$', re.MULTILINE)

    def get_text(self) -> str:
        """
        Strips preprocessor directives from the text.
        """
        text = self._source.get_text()
        text = self._CONDITIONAL_DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        text = self._OTHER_DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        return text


class MetaPFUnitProcessor(ABCMeta):
    def __str__(self) -> str:
        return "pFUnit preprocessor"


class PFUnitProcessor(TextProcessor, metaclass=MetaPFUnitProcessor):
    """
    Strips out pFUnit directives.
    """
    _DIRECTIVE_PATTERN = re.compile(r'^(\s*)(@\w+.*)$', re.MULTILINE)

    def get_text(self) -> str:
        """
        Strips processor directives from the text.
        """
        text = self._source.get_text()
        text = self._DIRECTIVE_PATTERN.sub(r'\1! \2', text)
        return text


class SourceTree(object, metaclass=ABCMeta):
    """
    Abstract parent of all actual language source files.
    """
    def __init__(self, text: SourceText) -> None:
        if not isinstance(text, SourceText):
            raise Exception('text argument must derive from SourceText.')

        self._text = text
        self._tree = None
        self._tree_error: Optional[str] = 'Not parsed yet'

    @abstractmethod
    def get_tree(self):
        """
        Gets a parse-tree representation of the source file.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_tree_error(self) -> Optional[str]:
        """
        Gets any errors raised while building the parse tree.
        """
        raise NotImplementedError()

    def get_text(self) -> str:
        """
        Gets the original source text.
        """
        return self._text.get_text()


class MetaFortranSource(ABCMeta):
    def __str__(self) -> str:
        return 'Fortran source'


class FortranSource(SourceTree, metaclass=MetaFortranSource):
    """
    Holds a Fortran source file as both a text block and parse tree.
    """
    def get_tree(self) -> Optional[Fortran2003.Program]:
        if not self._tree:
            # We don't use the tree directly. Instead we let all the decorators
            # have a go first.
            reader = readfortran.FortranStringReader(self._text.get_text(),
                                                     ignore_comments=False)
            # Pycharm complains about a type mismatch at this point but MyPy
            # doesn't.
            #
            fortran_parser: Type[Fortran2003.Program] \
                = ParserFactory().create(std='f2008')
            try:
                self._tree: Fortran2003.Program = fortran_parser(reader)
                self._tree_error = None
            except FparserException as ex:
                self._tree = None
                self._tree_error = str(ex)
        return self._tree

    def get_tree_error(self) -> Optional[str]:
        return self._tree_error

    def get_first_statement(self,
                            root: Optional[Fortran2003.Block] = None) \
            -> Fortran2003.StmtBase:
        """
        Gets the first "statement" part of the syntax tree or part thereof.

        @param root Optionally specify a subtree to use.
        """
        if not root:
            root = self._tree.content

        root = [root]

        while root:
            candidate = root.pop(0)
            if isinstance(candidate, Fortran2003.StmtBase):
                return candidate

            if isinstance(candidate, Fortran2003.BlockBase):
                root.extend(candidate.content)
            elif isinstance(candidate, Fortran2003.SequenceBase):
                root.extend(candidate.items)
            elif isinstance(candidate, Fortran2003.Comment):
                pass
            else:
                message = 'Unexpected candidate type: {0}'
                raise Exception(message.format(candidate.__class__.__name__))
        raise StylistException("Block without any statements.")

    def path(self,
             path: Union[Iterable, str],
             root: Optional[Fortran2003.Block] = None) \
            -> List[Fortran2003.Base]:
        """
        Returns the tree nodes described by the given path.

        @todo This functionality might be provided by fparser at some point

        @param path The path may be either a list of node name strings or a '/'
                    delimited string of node names.
        @param root Optionally specify a subtree to use.
        @return List of tree nodes or empty list.
        """
        if isinstance(path, str):
            path = path.split('/')
        else:
            path = list(path)

        found: List[Fortran2003.Base] = []
        if root:
            next_candidates = root
        else:
            tree = self.get_tree()
            if tree is None:
                return []
            else:
                next_candidates = list(tree.content)

        while path:
            node_name = path.pop(0)
            node_class = eval('Fortran2003.' + node_name)

            candidates = next_candidates
            next_candidates = []
            while candidates:
                candidate = candidates.pop(0)
                candidate_name = candidate.__class__.__name__
                node_subclasses = node_class.subclass_names
                # Only allow comments to be considered if we are looking for
                # a comment.
                if not isinstance(node_class, Fortran2003.Comment):
                    if 'Comment' in node_subclasses:
                        node_subclasses.remove('Comment')

                if self._ast_match(candidate, node_class):
                    if not path:  # Bottom of the path
                        found.append(candidate)

                    if isinstance(candidate,
                                  Fortran2003.BlockBase):
                        next_candidates.extend(candidate.content)
                    elif isinstance(candidate,
                                    Fortran2003.SequenceBase):
                        next_candidates.extend(candidate.items)
                    elif isinstance(candidate,
                                    Fortran2003.StmtBase):
                        pass
                    elif isinstance(candidate,
                                    Fortran2003.Comment):
                        pass
                    else:
                        message = 'Unexpected candidate type: {0}'
                        raise Exception(message.format(candidate_name))
        return found

    def find_all(self,
                 find_node: Type[Fortran2003.Base],
                 root: Fortran2003.Base = None) \
            -> Generator[Fortran2003.Base, None, None]:
        """
        Returns a generator which loops over all instances if the specified
        parse element below the root.

        The search descends the tree but that descent is terminated by a match.

        @todo This functionality might be provided by fparser at some point
        """
        if root:
            candidates = [root]
        else:
            tree = self.get_tree()
            if tree is None:
                return None
            else:
                candidates = list(tree.content)

        while candidates:
            candidate = candidates.pop(0)
            if self._ast_match(candidate, find_node):
                yield candidate
            else:  # If we found a thing we don't descend into it
                if isinstance(candidate, Fortran2003.BlockBase):
                    candidates.extend(candidate.content)
                elif isinstance(candidate,
                                Fortran2003.SequenceBase):
                    candidates.extend(candidate.items)
                else:
                    pass

    @staticmethod
    def _ast_match(candidate: Type[Fortran2003.Base],
                   sought_class: Type[Fortran2003.Base]) \
            -> bool:
        """
        Determines whether a node is a given type or a child thereof.
        """
        if candidate.__class__.__name__ == sought_class.__name__:
            return True

        considering = [sought_class]
        for consideration in considering:
            if candidate.__class__.__name__ == consideration.__name__:
                return True
            considering.extend([eval('Fortran2003.' + name)
                                for name in consideration.subclass_names])

        return False

    @staticmethod
    def print_tree(children: Fortran2003.Base,
                   indent: int = 0) -> None:
        """
        Dumps a textual representation of the tree to standard out.
        Intended for debug use.
        """
        # Argument "children" confuses Pycharm as it does not appear as
        # iterable even though it is. MyPy is not bothered.
        #
        for child in children:
            print(' ' * indent + child.__class__.__name__)
            if isinstance(child, Fortran2003.BlockBase):
                FortranSource.print_tree(child.content, indent+1)
            elif isinstance(child, Fortran2003.SequenceBase):
                FortranSource.print_tree(child.items, indent+1)


class MetaCSource(ABCMeta):
    def __str__(self) -> str:
        return "C source"


class CSource(SourceTree, metaclass=MetaCSource):
    """
    Holds a C/C++ source file as both a text block and parse tree.
    """
    def get_tree(self):
        raise NotImplementedError('C/C++ source is not supported yet.')

    def get_tree_error(self) -> Optional[str]:
        raise NotImplementedError('C/C++ source is not supported yet.')


class MetaPlainText(ABCMeta):
    def __str__(self) -> str:
        return "plain text"


class PlainText(SourceTree, metaclass=MetaPlainText):
    """
    Holds a plain text file as though it were source.
    """
    def get_tree(self) -> Generator[str, None, None]:
        for line in self.get_text().splitlines():
            yield line

    def get_tree_error(self) -> Optional[str]:
        return None


class _SourceChain(object):
    """
    Holds the chain of objects needed to understand a particular file
    extension.
    """
    def __init__(self,
                 extension: str,
                 parser: Type[SourceTree],
                 *preprocessors: Type[TextProcessor]) -> None:
        """
        Creates a SourceChain object from file extension and source objects.

        @param extension File extension which identifies this chain.
        @param parser Underlying language parser.
        @param preprocessors Any preprocessors to apply before parsing.
        """
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
    """
    Manages the handling of source file. Knows what chains of objects are
    needed to each file extension.
    """
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
    # On the other hand commodity means including the most commonly used
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
    def add_extension(cls,
                      extension: str,
                      source: Type[SourceTree],
                      *preprocessors: Type[TextProcessor]) -> None:
        """
        Adds a mapping between source file extension and source handling
        classes.

        @param extension File extension which identifies this chain.
        @param source Underlying language parser.
        @param preprocessors Any preprocessors to apply before parsing.
        """
        if extension in cls._extension_map:
            raise Exception('Extension "{}" already mapped to a handler'
                            .format(extension))

        cls._extension_map[extension] = _SourceChain(extension,
                                                     source,
                                                     *preprocessors)

    @classmethod
    def get_extensions(cls) -> Iterable[str]:
        """
        Gets the list of file extensions recognised by the read_file() method.
        """
        return cls._extension_map.keys()

    @classmethod
    def read_file(cls, source_file: Union[IO[str], str]) -> SourceTree:
        """
        Creates a Source object from a file.

        The file extension is used to determine the source type so this will
        not work on "files" which do not have a filename.
        """
        if isinstance(source_file, str):
            filename = source_file
        else:
            filename = source_file.name

        ext = os.path.splitext(filename)[1][1:]
        if ext not in cls._extension_map:
            raise Exception('Source file extension "{0}" not in handler map'
                            .format(ext))

        chain = cls._extension_map[ext]
        reader: SourceText = SourceFileReader(source_file)
        # Decorate reader
        for handler_class in chain.preprocessors:
            reader = handler_class(reader)

        return chain.parser(reader)
