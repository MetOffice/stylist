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
from typing import Any, List, Set, Type

import stylist.fortran
import stylist.issue
from stylist.rule import Rule
import stylist.source


class Style(object, metaclass=ABCMeta):
    """
    Abstract parent of all style lists.
    """
    def __init__(self, *rules: Rule) -> None:
        """
        :param *args: Rules which make up this style.
        """
        self._rules = list(rules)

    def list_rules(self) -> List[Rule]:
        """
        Gets a list of the rules which make up this style.
        """
        return self._rules

    def check(self,
              source: stylist.source.SourceTree) -> List[stylist.issue.Issue]:
        """
        Applies every rule in this style to a source code.

        :param source: Source code to inspect.
        :return: All issues found in the source.
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
