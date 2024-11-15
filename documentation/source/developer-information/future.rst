Ideas For Future Work
=====================

Any ideas for substantial future work should be documented on this page.

Parse Tree Traversal Efficiency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every rule is individually responsible for traversing its search space, be
that line-by-line for textual rules or node-by-node for parse tree rules.

This means the lines of the source file or nodes of the parse tree are
visited by each rule in turn. This could be inefficient. There may be a
means of turning this inside out and have each line or node visited only
once and each rule see the entity in turn.

See issue `#46`_ for me details.

.. _#46: https://github.com/MetOffice/stylist/issues/46

Coerce Code
~~~~~~~~~~~

At the moment the tool is able to highlight problems with the source code.
This is useful but for a sub-set of problems there is an obvious remedy
which could be enacted. For instance, a missing ``intent`` specification could
be fixed by imposing a default, e.g. ``intent none``.

Issue `#57`_ has more details.

.. _#57: https://github.com/MetOffice/stylist/issues/57

The general design is very similar to the existing one, outlined in the
:ref:`design-page`. The difference being that ``Rule`` objects can mutate the
parse tree as they go.

It may be necessary to have failing and non-failing issues. In this case a code
coercion would be reported as a non-failing issue which may be viewed or
suppressed. Faults which cannot be coerced would still raise failing issues which
cannot be ignored.

It's not clear how line-by-line text rules would mutate the text form and how
the resulting parse tree would be regenerated after they had.

And an example of operation:

.. uml:: uml/future_sequence_diagram.puml
    :caption: UML sequence diagram of example operation.
    :align: center
    :width: 100%
