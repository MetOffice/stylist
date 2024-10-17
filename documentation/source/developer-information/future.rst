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
which could be enacted. For instance, a missing `intent` specification could
be fixed by imposing a default `intent none`.

Issue `#57`_ has more details.

.. _#57: https://github.com/MetOffice/stylist/issues/57

A proposed design is given here:

.. uml:: uml/future_class_diagram.puml
    :caption: UML class diagram of potential coercive implementation.

And an example of operation:

.. uml:: uml/future_sequence_diagram.puml
    :caption: UML sequence diagram of example operation.
