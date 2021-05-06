#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Classes relating to styles made up of rules.
"""
from abc import ABCMeta
import logging
from typing import Any, Dict, List, Optional, Set, Type

from stylist import StylistException
from stylist.configuration import Configuration
import stylist.fortran
import stylist.issue
import stylist.rule
import stylist.source


class Style(object, metaclass=ABCMeta):
    """
    Abstract parent of all style lists.
    """
    def __init__(self, rules) -> None:
        if not isinstance(rules, list):
            rules = [rules]
        self._rules = rules

    def list_rules(self) -> List[str]:
        """
        Gets a list of the rules which make up this style.
        """
        return [rule.__class__.__name__ for rule in self._rules]

    def check(self,
              source: stylist.source.SourceTree) -> List[stylist.issue.Issue]:
        """
        Applies every rule in this style to the parse tree.

        source Program source code as an stylist.source.Source derived
               object.
        """
        logging.getLogger(__name__).info('Style: ' + self.__class__.__name__)
        issues: List[stylist.issue.Issue] = []
        for rule in self._rules:
            additional_issues = rule.examine(source)
            issues.extend(additional_issues)
            result = "Failed" if additional_issues else "Passed"
            message = f"Rule: {rule.__class__.__name__} - {result}"
            logging.getLogger(__name__).info(message)
        return issues


def _all_subclasses(cls: Any) -> Set[Type]:
    """
    Obtains the set of recursively all children of a class.
    """
    children: Set[Type] = set()
    to_examine = [cls]
    while len(to_examine) > 0:
        this_class = to_examine.pop()
        for child in this_class.__subclasses__():
            if child not in children:
                to_examine.append(child)
                children.add(child)
    return children


def determine_style(configuration: Configuration,
                    style_name: Optional[str] = None) -> Style:
    available_styles = configuration.available_styles()

    if style_name is None:
        if len(available_styles) == 1:
            style_name = available_styles[0]
        else:
            message = "Cannot pick a default style from file containing " \
                      "{0} styles"
            raise StylistException(message.format(len(available_styles)))

    if style_name not in available_styles:
        message = f"style '{style_name}' not found in configuration"
        raise StylistException(message)

    # Todo: It would be nice to remove abstracts from this list but I haven't
    #       worked out how yet.
    #
    potential_rules: Dict[str, Type[stylist.rule.Rule]] \
        = {cls.__name__: cls for cls in _all_subclasses(stylist.rule.Rule)}

    rules: List[stylist.rule.Rule] = []
    rule_list = configuration.get_style(style_name)
    if not isinstance(rule_list, list):
        raise TypeError('Style rules should be a list of names')
    for rule_description in rule_list:
        rule_name, _, rule_arguments_string = rule_description.partition('(')
        rule_name = rule_name.strip()
        rule_arguments_string, _, _ = rule_arguments_string.partition(')')
        rule_arguments: List[str] = []
        if rule_arguments_string.strip():
            rule_arguments = [thing.strip()
                              for thing in rule_arguments_string.split(',')]
        if rule_name not in potential_rules:
            raise StylistException(f"Unrecognised rule: {rule_name}")
        if rule_arguments:
            rules.append(potential_rules[rule_name](*rule_arguments))
        else:
            rules.append(potential_rules[rule_name]())
    return Style(rules)
