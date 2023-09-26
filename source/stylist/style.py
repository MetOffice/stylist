##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
"""
Classes relating to styles made up of rules.
"""
from abc import ABC
import logging
from typing import List

import stylist.fortran
import stylist.issue
from stylist.rule import Rule
import stylist.source


class Style(ABC):
    """
    Abstract parent of all style lists.
    """
    __unnamed_tally = 1

    def __init__(self, *rules: Rule) -> None:
        """
        :param rules: Rules which make up this style.
        """
        self.__rules = list(rules)
        self.__name = f"Unnamed style {self.__unnamed_tally}"
        self.__unnamed_tally += 1

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    def list_rules(self) -> List[Rule]:
        """
        Gets a list of the rules which make up this style.
        """
        return self.__rules

    def check(self,
              source: stylist.source.SourceTree) -> List[stylist.issue.Issue]:
        """
        Applies every rule in this style to a source code.

        :param source: Source code to inspect.
        :return: All issues found in the source.
        """
        logging.getLogger(__name__).info(f"Style: {self.name}")
        issues: List[stylist.issue.Issue] = []
        for rule in self.__rules:
            additional_issues = rule.examine(source)
            issues.extend(additional_issues)
            result = "Failed" if additional_issues else "Passed"
            message = f"Rule: {rule.__class__.__name__} - {result}"
            logging.getLogger(__name__).info(message)
        return issues
