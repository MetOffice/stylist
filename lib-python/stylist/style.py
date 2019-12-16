#!/usr/bin/env python
##############################################################################
# (c) Crown copyright 2019 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
##############################################################################
'''
Classes relating to styles made up of rules.
'''
from __future__ import absolute_import, division, print_function

from abc import ABCMeta
import logging

import stylist.issue
import stylist.rule


class Style(object):
    # pylint: disable=too-few-public-methods
    '''
    Abstract parent of all style lists.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, rules):
        if not isinstance(rules, list):
            rules = [rules]
        self._rules = rules

    def list_rules(self):
        '''
        Gets a list of the rules which make up this style.
        '''
        return [rule.__class__.__name__ for rule in self._rules]

    def check(self, source):
        '''
        Applies every rule in this style to the parse tree.

        source Program source code as an stylist.source.Source derived
               object.
        '''
        logging.getLogger(__name__).info('Style: ' + self.__class__.__name__)
        issues = []
        for rule in self._rules:
            issues.extend(rule.examine(source))
        return issues


class LFRicStyle(Style):
    # pylint: disable=too-few-public-methods
    '''
    LFRic project's list of rules.
    '''
    def __init__(self):
        rules = [stylist.rule.FortranCharacterset(),
                 stylist.rule.TrailingWhitespace(),
                 stylist.rule.MissingImplicit('none'),
                 stylist.rule.MissingOnly(ignore=['pfunit_mod', 'xios'])]
        super(LFRicStyle, self).__init__(rules)
