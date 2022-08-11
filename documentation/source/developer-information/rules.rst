Rules
=====

The abstract base of all rules is :py:class:`stylist.rule.Rule`. Classes
derived  from this implement an :py:func:`stylist.rule.Rule.examine` method
which is passed a :py:class:`stylist.source.SourceText` object. This allows
the source to be treated as a plain text file.

Rules relating to Fortran source may be found in the
:py:mod:`stylist.fortran` module. An abstract
:py:class:`stylist.fortran.FortranRule` is provided which requires an
:py:meth:`stylist.fortran.FortranRule.examine_fortran` method which is
passed a :py:class:`stylist.source.FortranSource` object. Thus the rule may
examine the Fortran parse tree.

Writing a New Text Rule
-----------------------

Just sub-class :py:class:`stylist.rule.Rule` and implement the
:py:meth:`stylist.rule.Rule.examine` method. Use the
:py:meth:`stylist.source.SourceText.get_text` method on the passed
:py:class:`stylist.source.SourceText` object to obtain the text of the source
file.

The "trailing white space" rule gives an example of using RegEx on the source
text. Meanwhile the "Fortran characterset" rule shows a more elaborate text
rule which implements a state-machine to test validity.

Writing a Fortran Rule
----------------------

An abstract :py:class:`stylist.rule.FortranRule` is provided, any new rule
should inherit from this and implement the
:py:meth:`stlist.rule.FortranRule.examine_fortran` method. Use the
:py:meth:`stylist.source.FortranSource.get_tree` method to obtain an fparser2
parse tree.

The :py:class:`stylist.source.FortranSource` class also provides some methods
for traversing the parse tree. It is expected that this functionality will
eventually become available through fparser2 and so will be removed from
stylist.

Documenting the Rule
--------------------

Don't forget to add your new rule to the user documentation. This is a
slightly clunky process involving adding some boilerplate to
``documentation/source/user-manual/rule-list.rst``.
