#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Rules relating to Fortran source.
"""
from typing import List

import fparser.two.Fortran2003 as Fortran2003
from stylist.issue import Issue
from stylist.rule import Rule, FortranRule


class FortranCharacterset(Rule):
    # pylint: disable=too-few-public-methods
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

    def examine(self, subject):
        # pylint: disable=too-many-branches
        """
        Examines the source code for none Fortran characters.

        This is complicated by the fact that the source must consist of only
        certain characters except comments and strings. These may contain
        anything.
        """
        issues = super(FortranCharacterset, self).examine(subject)

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
    # pylint: disable=too-few-public-methods
    """
    Catches cases where code blocks which could have an "implicit" statement
    don't.
    """

    def __init__(self, default='none'):
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

    _NATURE_MAP = {Fortran2003.Program_Stmt: 'Program',
                   Fortran2003.Module_Stmt: 'Module',
                   Fortran2003.Subroutine_Stmt: 'Subroutine',
                   Fortran2003.Function_Stmt: 'Function'}

    def examine_fortran(self, subject):
        issues = []

        scope_units = subject.path('Program_Unit')
        scope_units.extend(subject.path(['Main_Program',
                                         'Internal_Subprogram_Part',
                                         'Internal_Subprogram']))
        scope_units.extend(subject.path(['Module',
                                         'Module_Subprogram_Part',
                                         'Module_Subprogram']))
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
                issues.append(Issue(description))
        return issues


class MissingOnly(FortranRule):
    """
    Catches cases where a "use" statement is present but has no "only" claus.
    """

    def __init__(self, ignore=[]):
        """
        Constructs a "MissingOnly" rule object taking a list of exception
        modules which are not required to have an "only" clause.
        """
        assert isinstance(ignore, list)
        self._ignore = ignore

    def examine_fortran(self, subject):
        issues = []

        for statement in subject.find_all(Fortran2003.Use_Stmt):
            module = statement.items[2]
            onlies = statement.items[4]
            if str(module).lower() not in self._ignore:
                if onlies is None:
                    description = 'Usage of "{module}" without "only" clause.'
                    issues.append(Issue(description.format(module=module)))

        return issues


class MissingPointerInit(FortranRule):
    """
    Catches cases where a pointer is declared without being initialised.
    """

    def __init__(self, default='null()'):
        """
        Constructs a MissingPointerInit rule object taking a default
        assignment.

        Todo: Obviously the default is not used as we don't support coercing
              source at the moment.

        @param default: Target to be used if missing assignment found.
        """
        self._default = default

    def examine_fortran(self, subject):
        issues: List[Issue] = []

        candidates: List[Fortran2003.StmtBase] = []
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
        for statement in candidates:
            if isinstance(statement,  # Is variable
                          (Fortran2003.Data_Component_Def_Stmt,
                           Fortran2003.Type_Declaration_Stmt)):
                if isinstance(statement.parent.parent,
                              Fortran2003.Function_Subprogram):
                    # Is contained in a function
                    function_block: Fortran2003.Function_Subprogram \
                        = statement.parent.parent
                    suffix = function_block.children[0].items[3]
                    if isinstance(suffix, Fortran2003.Suffix):
                        if isinstance(suffix.items[0], Fortran2003.Name):
                            # Is return variable
                            return_variable = str(suffix.items[0])

            problem = 'Declaration of pointer "{0}" without initialisation.'

            attributes = statement.items[1]
            if attributes is None:
                continue
            cannon_attr = list(str(item).lower().replace(' ', '')
                               for item in attributes.items)
            argument_def = 'intent(in)' in cannon_attr \
                           or 'intent(out)' in cannon_attr \
                           or 'intent(inout)' in cannon_attr
            if 'pointer' in cannon_attr and not argument_def:
                for variable in statement.items[2].items:
                    if isinstance(statement,  # Is variable
                                  (Fortran2003.Data_Component_Def_Stmt,
                                   Fortran2003.Type_Declaration_Stmt)):
                        name = str(variable.items[0])
                        if name == return_variable:
                            continue  # Return variables cannot be initialised.
                        init = variable.items[3]
                        if init is None:
                            issues.append(Issue(problem.format(name)))
                    elif isinstance(statement,  # Is procedure
                                    (Fortran2003.Proc_Component_Def_Stmt,
                                     Fortran2003.Procedure_Declaration_Stmt)):
                        name = str(variable)
                        if isinstance(variable, Fortran2003.Name):
                            issues.append(Issue(problem.format(name)))
                    else:
                        message \
                            = f"Unexpected source element: {repr(statement)}"
                        raise Exception(message)

        issues.sort()
        return issues
