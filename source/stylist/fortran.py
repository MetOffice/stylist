##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Rules relating to Fortran source.
"""
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import (Container, Dict, List, Optional, Pattern, Sequence, Type,
                    Union)

import fparser.two.Fortran2003 as Fortran2003  # type: ignore
import fparser.two.Fortran2008 as Fortran2008  # type: ignore
from fparser.two.utils import (get_child as fp_get_child,  # type: ignore
                               walk as fp_walk)

from stylist.issue import Issue
from stylist.rule import Rule
from stylist.source import FortranSource


def _line(node: Fortran2003.Base) -> int:
    """
    Determines the source line on which a given node appears.

    Although the range of lines covered by a particular statement is available
    it doesn't seem to be possible to determine exactly which one a particular
    subsidiary part appears on. Therefore it is always the first line of the
    continuation block.
    """
    target = node
    while target.item is None:
        target = target.parent
    return target.item.span[0]


class FortranRule(Rule, ABC):
    """
    Parent for style rules pertaining to Fortran source.
    """

    def examine(self, subject: FortranSource) -> List[Issue]:
        """
        Base for rules which scruitinise the parse tree of Fortran source.

        :param subject: Source file to examine.
        :return: Issues found with the source.
        """
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

        :param subject: Source file to examine.
        :return: Issues found with the source.
        """
        raise NotImplementedError()


class FortranCharacterset(Rule):
    """
    Traps any characters which do not fall in the list of those allowed in
    Fortran source. This takes into account the fact that there is no
    restriction on what may appear in comments or strings.
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
    Catches cases where code blocks which could have an ``implicit`` statement
    don't.
    """

    def __init__(self,
                 require_everywhere: Optional[bool] = False) -> None:
        """
        :param require_everywhere: By default the rule checks only in places
            which require an ``implicit`` statement. Set this argument to check
            everywhere an ``implicit`` could exist.
        """
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
        filtered_units = filter(lambda s: not isinstance(s,
                                                         Fortran2003.Comment),
                                scope_units)
        scope: Fortran2003.Block
        for scope in filtered_units:
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
                issues.append(Issue(description, line=_line(scope_statement)))
        return issues


class MissingIntent(FortranRule):
    """
    Catches cases where a function or subroutine's dummy arguments don't
    have specified intent.
    """

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []
        scope_units: List[Fortran2003.Base] = []

        # get all subprograms (functions and subroutines) within programs
        scope_units.extend(subject.path(['Main_Program',
                                         'Internal_Subprogram_Part',
                                         'Internal_Subprogram']))

        # get all subprograms within modules
        scope_units.extend(subject.path(['Module',
                                         'Module_Subprogram_Part',
                                         'Module_Subprogram']))

        # get all naked subprograms
        scope_units.extend(subject.path(['Function_Subprogram']))
        scope_units.extend(subject.path(['Subroutine_Subprogram']))

        for scope in scope_units:
            # get initialisation statement and piece containing all type
            # declarations

            specs = None
            for part in scope.children:
                if type(part) in (Fortran2003.Function_Stmt,
                                  Fortran2003.Subroutine_Stmt):
                    stmt = part
                if type(part) == Fortran2003.Specification_Part:
                    specs = part
                    # we don't need to check the rest of the children
                    break

            # covert tree node into a python list
            dummy_arg_list = stmt.children[2]

            # initialise set in case empty
            dummy_args: List[str] = []
            if dummy_arg_list is not None:
                dummy_args = [arg.string.lower() for arg in
                              dummy_arg_list.children]

            if specs is not None:
                for spec in specs.children:
                    if spec.__class__ == Fortran2008.Type_Declaration_Stmt:

                        # check if type declaration has an intent
                        attributes = spec.children[1]
                        if attributes is not None:
                            for attribute in attributes.children:
                                if attribute.__class__ \
                                        == Fortran2003.Intent_Attr_Spec:

                                    # if so, remove argument names from
                                    # dummy_args
                                    for arg in spec.children[2].children:
                                        arg_name = arg.children[
                                            0].string.lower()
                                        if arg_name in dummy_args:
                                            dummy_args.remove(arg_name)

                    elif spec.__class__ \
                            == Fortran2003.Procedure_Declaration_Stmt:
                        print(repr(spec))
                        attributes = spec.children[1]
                        if attributes is not None:
                            for attribute in attributes.children:
                                if attribute.__class__ \
                                        == Fortran2003.Proc_Attr_Spec:
                                    # if so, remove argument names from
                                    # dummy_args
                                    for arg in spec.children[2].children:
                                        arg_name = arg.string.lower()
                                        if arg_name in dummy_args:
                                            dummy_args.remove(arg_name)

            # get the type of block
            if type(scope) == Fortran2003.Subroutine_Subprogram:
                unit_type = 'subroutine'
            elif type(scope) == Fortran2003.Function_Subprogram:
                unit_type = 'function'

            # any remaining dummy arguments lack intent
            for arg in dummy_args:
                description = f'Dummy argument "{arg}" of {unit_type} "' \
                              f'{stmt.children[1].string}" is missing an ' \
                              f'"intent" statement'
                issues.append(Issue(description, line=_line(stmt)))

        return issues


class MissingOnly(FortranRule):
    """
    Catches cases where a "use" statement is present but has no "only" clause.
    """

    def __init__(self, ignore: Optional[List[str]] = None) -> None:
        """
        :param ignore: List of module names which are not required to have an
                       "only" clause.
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
                                        line=_line(statement)))

        return issues


class IntrinsicModule(FortranRule):
    """
    Catches cases where an intrinsic module is used with the "intrinsic"
    keyword ommitted.
    """
    _INTRINSICS = ["iso_c_binding", "iso_fortran_env",
                   "ieee_exceptions", "ieee_arithmetic",
                   "ieee_features"]

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues = []
        for statement in subject.find_all(Fortran2003.Use_Stmt):
            module = statement.items[2]
            if str(module).lower() in self._INTRINSICS:
                nature = statement.items[0]
                if nature is None or nature.string.lower() != 'intrinsic':
                    description = 'Usage of intrinsic module "{module}" ' \
                                  'without "intrinsic" clause.'
                    issues.append(Issue(description.format(module=module),
                                        line=_line(statement)))

        return issues


class LabelledDoExit(FortranRule):
    """
    Catches cases where a "do" construct is exited but not explicitly named.
    """

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues = []

        for exit in subject.find_all(Fortran2003.Exit_Stmt):
            if exit.items[1] is None:
                issues.append(Issue('Usage of "exit" without label indicating '
                                    'which "do" construct is being exited '
                                    'from.',
                                    line=_line(exit)))

        # Above doesn't catch exits in inline if statements
        for statement in subject.find_all(Fortran2003.If_Stmt):
            action = statement.items[1]
            if type(action) == Fortran2003.Exit_Stmt and action.items[
                    1] is None:
                issues.append(Issue('Usage of "exit" without label indicating '
                                    'which "do" construct is being exited '
                                    'from.',
                                    line=_line(statement)))

        return issues


class MissingPointerInit(FortranRule):
    """
    Catches cases where a pointer is declared without being initialised.
    """
    problem = 'Declaration of pointer "{name}" without initialisation.'

    @staticmethod
    def _is_pointer(root: Fortran2003.Base,
                    attr_node: Type[Fortran2003.Base]) -> bool:
        attribute_names: List[str] = []
        for attribute in fp_walk(root, attr_node):
            attribute_names.append(str(attribute).strip())
        return 'POINTER' in attribute_names

    @staticmethod
    def _data(root: Fortran2003.Base,
              declaration_statement: Type[Fortran2003.Base],
              attribute_specification: Type[Fortran2003.Base],
              entity_declaration: Type[Fortran2003.Base],
              initialiser: Type[Fortran2003.Base],
              ignore_names: Sequence[str] = ()) -> List[Issue]:
        issues: List[Issue] = []

        for data_declaration in fp_walk(root, declaration_statement):
            if not MissingPointerInit._is_pointer(data_declaration,
                                                  attribute_specification):
                continue

            for entity in fp_walk(data_declaration, entity_declaration):
                if str(fp_get_child(entity, Fortran2003.Name)) in ignore_names:
                    continue

                if fp_get_child(entity, initialiser) is None:
                    name = str(fp_get_child(entity, Fortran2003.Name))
                    message = MissingPointerInit.problem.format(name=name)
                    issue = Issue(message, line=data_declaration.item.span[0])
                    issues.append(issue)

        return issues

    @staticmethod
    def _proc(root: Fortran2003.Base,
              declaration_statement: Type[Fortran2003.Base],
              attribute_specification: Type[Fortran2003.Base],
              declaration_list: Type[Fortran2003.Base],
              ignore_names: Container[str] = ()) -> List[Issue]:
        issues: List[Issue] = []

        for proc_declaration in fp_walk(root, declaration_statement):
            if not MissingPointerInit._is_pointer(proc_declaration,
                                                  attribute_specification):
                continue

            for declaration in fp_get_child(proc_declaration,
                                            declaration_list).children:
                if (isinstance(declaration, Fortran2003.Name)
                        and str(declaration) not in ignore_names):
                    name = str(declaration)
                    message = MissingPointerInit.problem.format(name=name)
                    issue = Issue(message, line=proc_declaration.item.span[0])
                    issues.append(issue)

        return issues

    @staticmethod
    def _program_unit(unit: Union[Fortran2003.Main_Program,
                                  Fortran2003.Module]) -> List[Issue]:
        issues: List[Issue] = []

        specification = fp_get_child(unit, Fortran2003.Specification_Part)

        issues.extend(MissingPointerInit._data(
            specification,
            Fortran2003.Type_Declaration_Stmt,
            Fortran2003.Attr_Spec,
            Fortran2003.Entity_Decl,
            Fortran2003.Initialization)
        )
        issues.extend(MissingPointerInit._proc(
            specification,
            Fortran2003.Procedure_Declaration_Stmt,
            Fortran2003.Proc_Attr_Spec,
            Fortran2003.Proc_Decl_List)
        )

        return issues

    @staticmethod
    def _derived_type_definition(derived_type: Fortran2003.Derived_Type_Def)\
            -> List[Issue]:
        issues: List[Issue] = []

        issues.extend(MissingPointerInit._data(
            derived_type,
            Fortran2003.Data_Component_Def_Stmt,
            Fortran2003.Component_Attr_Spec,
            Fortran2003.Component_Decl,
            Fortran2003.Component_Initialization)
        )
        issues.extend(MissingPointerInit._proc(
            derived_type,
            Fortran2003.Proc_Component_Def_Stmt,
            Fortran2003.Proc_Component_Attr_Spec,
            Fortran2003.Proc_Decl_List)
        )

        return issues

    @staticmethod
    def _subroutine_definition(subroutine: Fortran2003.Subroutine_Subprogram)\
            -> List[Issue]:
        issues: List[Issue] = []

        subroutine_statement = fp_get_child(subroutine,
                                            Fortran2003.Subroutine_Stmt)
        arguments = fp_get_child(subroutine_statement,
                                 Fortran2003.Dummy_Arg_List)
        argument_names = [str(name) for name in fp_walk(arguments,
                                                        Fortran2003.Name)]

        issues.extend(MissingPointerInit._data(
            subroutine,
            Fortran2003.Type_Declaration_Stmt,
            Fortran2003.Attr_Spec,
            Fortran2003.Entity_Decl,
            Fortran2003.Initialization,
            argument_names)
        )
        issues.extend(MissingPointerInit._proc(
            subroutine,
            Fortran2003.Procedure_Declaration_Stmt,
            Fortran2003.Proc_Attr_Spec,
            Fortran2003.Proc_Decl_List,
            argument_names)
        )

        return issues

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []

        unit: Union[Fortran2003.Main_Program, Fortran2003.Module]
        for unit in fp_walk(subject.get_tree(),
                            (Fortran2003.Main_Program,
                             Fortran2003.Module)):
            issues.extend(self._program_unit(unit))

        subroutine: Fortran2003.Subroutine_Subprogram
        for subroutine in subject.find_all(Fortran2003.Subroutine_Subprogram):
            issues.extend(self._subroutine_definition(subroutine))

        derived_type: Fortran2003.Derived_Type_Def
        for derived_type in subject.find_all(Fortran2003.Derived_Type_Def):
            issues.extend(self._derived_type_definition(derived_type))

        issues.sort(key=lambda x: (x.filename, x.line, x.description))
        return issues


class KindPattern(FortranRule):
    """
    Ensures kind names match a specified pattern.
    """
    _ISSUE_TEMPLATE = "Kind '{kind}' found for {type} variable '{name}' does" \
                      " not fit the pattern /{pattern}/."

    def __init__(self, *,  # There are no positional arguments.
                 integer: Union[str, Pattern],
                 real: Union[str, Pattern]):
        """
        Patterns are set only for integer and real data types however Fortran
        supports many more. Logical and Complex for example. For those cases a
        default pattern of ".*" is used to accept anything.

        :param integer: Regular expression which integer kinds must match.
        :param real: Regular expression which real kinds must match.
        """
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
                    kind: str = str(kind_selector.children[1])
                    match = self._patterns[data_type].match(kind)
                    if match is None:
                        entity_declaration = candidate.items[2]
                        message = self._ISSUE_TEMPLATE.format(
                            type=data_type,
                            kind=kind,
                            name=entity_declaration,
                            pattern=self._patterns[data_type].pattern)
                        issues.append(Issue(message,
                                            line=_line(candidate)))

        issues.sort(key=lambda x: (x.filename, x.line, x.description))
        return issues


class AutoCharArrayIntent(FortranRule):
    """
    Checks that all automatically assigned character arrays used as
    subroutine or function arguments have intent(in) to avoid writing
    outside the given array.
    """
    def _message(self, name, intent):
        return (f"Arguments of type character(*) must have intent IN, but "
                f"{name} has intent {intent}.")

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []

        # Collect all variable declarations
        declarations: List[Fortran2003.Type_Declaration_Stmt] = list(
            subject.find_all(Fortran2003.Type_Declaration_Stmt)
        )

        # keep only the ones in subroutines
        declarations = [
            declaration
            for declaration
            in declarations
            if isinstance(
                declaration.parent.parent,
                Fortran2003.Subroutine_Subprogram
            )
        ]

        for declaration in declarations:
            type_spec = declaration.items[0]
            # If not a character, no concern
            if not type_spec.items[0] == "CHARACTER":
                continue
            param_value = type_spec.items[1]
            # This might be a length selector, if so get the param value
            if isinstance(param_value, Fortran2003.Length_Selector):
                param_value = param_value.items[1]
            # If not an auto length, no concern
            if not param_value.string == "*":
                continue
            attr_spec_list = declaration.items[1]
            # If no attributes specified, no concern
            if attr_spec_list is None:
                continue
            # Get intent attr and not other attributes
            intent_attr = None
            for item in attr_spec_list.items:
                if isinstance(item, Fortran2003.Intent_Attr_Spec):
                    intent_attr = item
                    break
            # If no intent, no concern
            # Ensuring arguments specify intent should be enforced elsewhere
            if intent_attr is None:
                continue
            # Intent in, no concern
            if intent_attr.items[1].string == "IN":
                continue
            issues.append(Issue(
                self._message(
                    declaration.items[2].string,
                    intent_attr.items[1]
                ),
                line=_line(declaration)
            ))

        return issues


class NakedLiteral(FortranRule):
    """
    Checks that all literal values have their kind specified.

    Checking of integers and reals are controlled separately so you can have
    one and not the other.
    """
    def __init__(self, integers: bool = True, reals: bool = True):
        self._integers = integers
        self._reals = reals

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []

        candidates: List[Fortran2003.Base] = []
        if self._integers:
            candidates.extend(fp_walk(subject.get_tree(),
                                      Fortran2003.Int_Literal_Constant))
        if self._reals:
            candidates.extend(fp_walk(subject.get_tree(),
                                      Fortran2003.Real_Literal_Constant))

        for constant in candidates:
            if constant.items[1] is None:
                if isinstance(constant.parent, Fortran2003.Assignment_Stmt):
                    name = str(fp_get_child(constant.parent, Fortran2003.Name))
                    message = f'Literal value assigned to "{name}"' \
                              ' without kind'
                elif isinstance(constant.parent.parent,
                                (Fortran2003.Entity_Decl,
                                 Fortran2003.Component_Decl)):
                    name = str(fp_get_child(constant.parent.parent,
                                            Fortran2003.Name))
                    message = f'Literal value assigned to "{name}"' \
                              ' without kind'
                else:
                    message = 'Literal value without "kind"'
                issues.append(Issue(message, line=_line(constant)))

        return issues


class ForbidUsage(FortranRule):
    """
    Checks that no attempt is made to use the specific module unless it is in
    one of the excepted modules.
    """
    def __init__(self,
                 name: str,
                 exceptions: Sequence[Union[str, Pattern]] = ()):
        """
        :param name: Name of module to forbid.
        :param exceptions: names (or name patterns) in which module may be
                           used.
        """
        self._forbidden_module = name
        self._exceptions: List[Pattern] = []
        for exception in exceptions:
            if isinstance(exception, Pattern):
                self._exceptions.append(exception)
            else:
                self._exceptions.append(re.compile(exception))

    def examine_fortran(self, subject: FortranSource) -> List[Issue]:
        issues: List[Issue] = []
        for module_statement in subject.find_all(Fortran2003.Module_Stmt):
            in_module = str(module_statement.items[1])
            for use in subject.find_all(Fortran2003.Use_Stmt,
                                        module_statement.parent):
                use_module = str(use.items[2])
                forbidden = (use_module == self._forbidden_module)
                for exception_pattern in self._exceptions:
                    forbidden = (forbidden
                                 and not exception_pattern.match(in_module))
                if forbidden:
                    message = f"Attempt to use forbidden module '{use_module}'"
                    issues.append(Issue(message, line=use.item.span[0]))
        return issues
