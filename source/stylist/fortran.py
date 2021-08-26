##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Rules relating to Fortran source.
"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import re
from typing import Dict, List, Optional, Pattern, Type, Union

import fparser.two.Fortran2003 as Fortran2003  # type: ignore

from stylist.issue import Issue
from stylist.rule import Rule
from stylist.source import FortranSource


class FortranRule(Rule, metaclass=ABCMeta):
    """
    Parent for style rules pertaining to Fortran source.
    """
    def examine(self, subject: FortranSource) -> List[Issue]:
        issues = []
        if not isinstance(subject, FortranSource):
            description = 'Non-Fortran source passed to a Fortran rule'
            raise Exception(description)

        if not subject.get_tree():
            description = "Unable to perform {} as source didn't parse: {}"
            issues.append(Issue(description.format(self.__class__.__name__,
                                                   subject.get_tree_error())))
            return issues

        issues.extend(self.examine_fortran(subject))
        return issues

    @abstractmethod
    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        """
        Examines the provided Fortran source code object for an issue.

        Returns a list of stylist.issue.Issue objects.
        """
        raise NotImplementedError()


class FortranCharacterset(Rule):
    """
    Scans the source for characters which are not supported by Fortran.
    """
    _FORTRAN_LETTER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    _FORTRAN_DIGIT = '0123456789'
    _FORTRAN_ALPHANUMERIC = _FORTRAN_LETTER + _FORTRAN_DIGIT + '_'
    _FORTRAN_SPECIALS = ' =+-*/\\()[]{},.:;!"%&~<>?\'`^|$#@'
    _FORTRAN_CHARACTERSET = _FORTRAN_ALPHANUMERIC + _FORTRAN_SPECIALS

    _APOSTROPHY = "'"
    _EXCLAMATION = '!'
    _NEWLINE = '\n'
    _QUOTE = '"'

    def examine(self, subject: FortranSource) -> List[Issue]:
        """
        Examines the source code for none Fortran characters.

        This is complicated by the fact that the source must consist of only
        certain characters except comments and strings. These may contain
        anything.
        """
        issues = []

        text = subject.get_text()
        index = 0
        line = 1
        state = 'code'
        while index < len(text):
            character = text[index]
            if state == 'code':
                if character == self._NEWLINE:
                    line += 1
                elif character == self._EXCLAMATION:
                    state = 'comment'
                elif character == self._APOSTROPHY:
                    state = 'apostraphystring'
                elif character == self._QUOTE:
                    state = 'quotestring'
                elif character in self._FORTRAN_CHARACTERSET:
                    pass
                else:
                    description = "Found character {char} " \
                                  + "not in Fortran character set"
                    description = description.format(char=repr(character))
                    issues.append(Issue(description, line=line))
            elif state == 'comment':
                if character == self._NEWLINE:
                    line += 1
                    state = 'code'
            elif state == 'apostraphystring':
                if character == self._APOSTROPHY:
                    state = 'code'
            elif state == 'quotestring':
                if character == self._QUOTE:
                    state = 'code'
            else:
                raise Exception('Parser in unknown state: ' + state)
            index += 1

        return issues


class MissingImplicit(FortranRule):
    """
    Catches cases where code blocks which could have an "implicit" statement
    don't.
    """
    def __init__(self, default='none', require_everywhere=False) -> None:
        """
        Constructor taking a default implication.

        Todo: This rule was designed to check merely for the presence of an
        "implicit" statement but to leave the choice of implication to the
        user. It might also be desirable to allow this rule to enforce a
        specific implication. In which case the "default" argument may need a
        different name. A switch would be necessary to flip between "any" and
        "specific" modes.

        Todo: At the moment the default is not used. In the future we may want
        to allow rules to enforce style rather than simply reporting it. In
        this case the default would be used where none is present.
        """
        assert default.lower() in ('none', 'private', 'public')
        self._default = default.lower()
        self._require_everywhere = require_everywhere

    _NATURE_MAP: Dict[Type[Fortran2003.StmtBase], str] \
        = {Fortran2003.Program_Stmt: 'Program',
           Fortran2003.Module_Stmt: 'Module',
           Fortran2003.Subroutine_Stmt: 'Subroutine',
           Fortran2003.Function_Stmt: 'Function'}

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues = []

        scope_units = subject.path('Program_Unit')
        if self._require_everywhere:
            scope_units.extend(subject.path(['Main_Program',
                                             'Internal_Subprogram_Part',
                                             'Internal_Subprogram']))
            scope_units.extend(subject.path(['Module',
                                             'Module_Subprogram_Part',
                                             'Module_Subprogram']))
        scope: Fortran2003.Block
        for scope in scope_units:
            scope_statement = subject.get_first_statement(root=scope)

            implication = subject.path(['Specification_Part',
                                        'Implicit_Part',
                                        'Implicit_Stmt'],
                                       root=scope.content[1:])
            if not implication:
                nature = MissingImplicit._NATURE_MAP[scope_statement.__class__]
                name = scope_statement.items[1]
                description = "{thing} '{name}' is missing " \
                              + "an implicit statement"
                description = description.format(thing=nature, name=name)
                issues.append(Issue(description,
                                    line=scope_statement.item.span[0]))
        return issues


class MissingOnly(FortranRule):
    """
    Catches cases where a "use" statement is present but has no "only" claus.
    """
    def __init__(self, ignore: Optional[List[str]] = None) -> None:
        """
        Constructs a "MissingOnly" rule object taking a list of exception
        modules which are not required to have an "only" clause.
        """
        if ignore is None:
            self._ignore = []
        else:
            self._ignore = ignore

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues = []

        for statement in subject.find_all(Fortran2003.Use_Stmt):
            module = statement.items[2]
            onlies = statement.items[4]
            if str(module).lower() not in self._ignore:
                if onlies is None:
                    description = 'Usage of "{module}" without "only" clause.'
                    issues.append(Issue(description.format(module=module),
                                        line=statement.item.span[0]))

        return issues


class MissingPointerInit(FortranRule):
    """
    Catches cases where a pointer is declared without being initialised.
    """

    def __init__(self, default='null()') -> None:
        """
        Constructs a MissingPointerInit rule object taking a default
        assignment.

        Todo: Obviously the default is not used as we don't support coercing
              source at the moment.

        @param default: Target to be used if missing assignment found.
        """
        self._default = default

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []

        candidates: List[Fortran2003.Base] = []
        # Component variables
        candidates.extend(
            subject.find_all(Fortran2003.Data_Component_Def_Stmt))
        # Component Procedure
        candidates.extend(
            subject.find_all(Fortran2003.Proc_Component_Def_Stmt))
        # Procedure declaration
        candidates.extend(
            subject.find_all(Fortran2003.Procedure_Declaration_Stmt))
        # Variable declaration
        candidates.extend(
            subject.find_all(Fortran2003.Type_Declaration_Stmt))

        return_variable = ''
        for candidate in candidates:
            if isinstance(candidate,  # Is variable
                          (Fortran2003.Data_Component_Def_Stmt,
                           Fortran2003.Type_Declaration_Stmt)):
                if isinstance(candidate.parent.parent,
                              Fortran2003.Function_Subprogram):
                    # Is contained in a function
                    function_block: Fortran2003.Function_Subprogram \
                        = candidate.parent.parent
                    statement = None
                    for thing in function_block.children:
                        if isinstance(thing, Fortran2003.Function_Stmt):
                            statement = thing
                            break
                    if statement is None:
                        message = "Malformed parse tree: Function subprogram" \
                                  " without Function statement"
                        raise Exception(message)
                    suffix = statement.items[3]
                    if isinstance(suffix, Fortran2003.Suffix):
                        if isinstance(suffix.items[0], Fortran2003.Name):
                            # Is return variable
                            return_variable = str(suffix.items[0])

            problem = 'Declaration of pointer "{name}" without initialisation.'

            attributes = candidate.items[1]
            if attributes is None:
                continue
            cannon_attr = list(str(item).lower().replace(' ', '')
                               for item in attributes.items)
            argument_def = 'intent(in)' in cannon_attr \
                           or 'intent(out)' in cannon_attr \
                           or 'intent(inout)' in cannon_attr
            if 'pointer' in cannon_attr and not argument_def:
                for variable in candidate.items[2].items:
                    if isinstance(candidate,  # Is variable
                                  (Fortran2003.Data_Component_Def_Stmt,
                                   Fortran2003.Type_Declaration_Stmt)):
                        name = str(variable.items[0])
                        if name == return_variable:
                            continue  # Return variables cannot be initialised.
                        init = variable.items[3]
                        if init is None:
                            message = problem.format(name=name)
                            line_number = candidate.item.span[0]
                            issues.append(Issue(message, line=line_number))
                    elif isinstance(candidate,  # Is procedure
                                    (Fortran2003.Proc_Component_Def_Stmt,
                                     Fortran2003.Procedure_Declaration_Stmt)):
                        name = str(variable)
                        if isinstance(variable, Fortran2003.Name):
                            line_number = candidate.item.span[0]
                            message = problem.format(name=name)
                            issues.append(Issue(message, line=line_number))
                    else:
                        message \
                            = f"Unexpected source element: {repr(candidate)}"
                        raise Exception(message)

        issues.sort(key=lambda x: (x.filename, x.line, x.description))
        return issues


class KindPattern(FortranRule):
    _ISSUE_TEMPLATE = "Kind '{kind}' found for {type} variable '{name}' does" \
            " not fit the pattern /{pattern}/."

    def __init__(self, *,  # There are no positional arguments.
                 integer: Union[str, Pattern],
                 real: Union[str, Pattern]):
        # We only set patterns for integer and real data types however Fortran
        # supports many more. e.g. Logical and Complex. In those cases we
        # accept anything by having a default pattern of ".*"
        #
        self._patterns: Dict[str, Pattern] \
            = defaultdict(lambda: re.compile(r'.*'))
        if isinstance(integer, str):
            self._patterns['integer'] = re.compile(integer)
        else:
            self._patterns['integer'] = integer
        if isinstance(real, str):
            self._patterns['real'] = re.compile(real)
        else:
            self._patterns['real'] = real

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []

        candidates: List[Fortran2003.Base] = []
        # Component variables
        candidates.extend(
            subject.find_all(Fortran2003.Data_Component_Def_Stmt))
        # Component Procedure
        candidates.extend(
            subject.find_all(Fortran2003.Proc_Component_Def_Stmt))
        # Procedure declaration
        candidates.extend(
            subject.find_all(Fortran2003.Procedure_Declaration_Stmt))
        # Variable declaration
        candidates.extend(
            subject.find_all(Fortran2003.Type_Declaration_Stmt))

        for candidate in candidates:
            if isinstance(candidate,  # Is variable
                          (Fortran2003.Data_Component_Def_Stmt,
                           Fortran2003.Type_Declaration_Stmt)):
                type_spec: Fortran2003.Intrinsic_Type_Spec = candidate.items[0]
                kind_selector: Fortran2003.Kind_Selector = type_spec.items[1]

                if isinstance(kind_selector, Fortran2003.Kind_Selector):
                    data_type: str = type_spec.items[0].lower()
                    kind: str = kind_selector.string.strip('()')
                    match = self._patterns[data_type].match(kind)
                    if match is None:
                        entity_declaration = candidate.items[2]
                        message = self._ISSUE_TEMPLATE.format(
                            type=data_type,
                            kind=kind,
                            name=entity_declaration,
                            pattern=self._patterns[data_type].pattern)
                        issues.append(Issue(message,
                                            line=candidate.item.span[0]))

        issues.sort(key=lambda x: (x.filename, x.line, x.description))
        return issues
