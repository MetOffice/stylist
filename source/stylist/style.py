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
import configparser
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from stylist import StylistException
import stylist.fortran
import stylist.issue
import stylist.rule
import stylist.source


class Style(object, metaclass=ABCMeta):
    # pylint: disable=too-few-public-methods
    """
    Abstract parent of all style lists.
    """
    def __init__(self, rules):
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
            issues.extend(rule.examine(source))
        return issues


def _all_subclasses(cls):
    children = set()
    to_examine = [cls]
    while len(to_examine) > 0:
        this_class = to_examine.pop()
        for child in this_class.__subclasses__():
            if child not in children:
                to_examine.append(child)
                children.add(child)
    return children


def read_style(rule_file: Path, style_name: Optional[str] = None) -> Style:
    PREFIX = 'style.'

    configuration = configparser.ConfigParser()
    try:
        with rule_file.open('rt') as handle:
            configuration.read_file(handle)
    except configparser.MissingSectionHeaderError:
        pass  # It is not an error to have an empty configuration file.

    available_styles = [section[len(PREFIX):]
                        for section in configuration.sections()
                        if section.startswith(PREFIX)]

    if style_name is None:
        if len(available_styles) == 1:
            style_name = available_styles[0]
        else:
            message = "Cannot pick a default style from file containing " \
                      "{0} styles"
            raise StylistException(message.format(len(available_styles)))

    if style_name not in available_styles:
        message = f"style {style_name} not found in configuration"
        raise StylistException(message)

    # Todo: It would be nice to remove abstracts from this list but I haven't
    #       worked out how yet.
    #
    potential_rules: Dict[str, Type[stylist.rule.Rule]] \
        = {cls.__name__: cls for cls in _all_subclasses(stylist.rule.Rule)}

    rules: List[stylist.rule.Rule] = []
    rule_string = configuration['style.' + style_name]['rules']
    for rule_description in rule_string.split(','):
        rule_name, _, rule_arguments = rule_description.partition('(')
        rule_name = rule_name.strip()
        rule_arguments, _, _ = rule_arguments.partition(')')
        if rule_arguments.strip():
            rule_arguments = [thing.strip()
                              for thing in rule_arguments.split(',')]
        if rule_name not in potential_rules:
            raise StylistException(f"Unrecognised rule: {rule_name}")
        if rule_arguments:
            rules.append(potential_rules[rule_name](*rule_arguments))
        else:
            rules.append(potential_rules[rule_name]())
    return Style(rules)
