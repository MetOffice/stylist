.. _design-page:

Design
======

The fundamental building block of Stylist is the "Rule." Each rule implements
a single check which the source code must pass.

.. uml::  uml/rule_class.puml
    :caption: UML class diagram showing "rule" module classes.
    :align: center
    :width: 100%

Rules are collected into "Styles" allowing different sets of rules to be used
for different purposes.

.. uml::  uml/style_class.puml
    :caption: UML class diagram showing "style" module classes.
    :align: center
    :width: 100%

Source is presented either line-by-line as strings from the text file or as an
abstract syntax tree, gained by parsing the source.

.. uml:: uml/source_class.puml
    :caption: UML class diagram showing "source" module classes.
    :align: center
    :width: 100%

The line based ``SourceText`` can come from either a file or a string buffer.
This text can have preprocessors applied to it using the decorator pattern.

Operation is orchestrated through the ``Engine`` class. It makes use of a
factory class to create the correct source object from a file.

.. uml:: uml/engine_class.puml
    :caption: UML class diagram showing various orchestration classes.
    :align: center
    :width: 100%

Sample operation is shown in the following sequence diagram:

.. uml:: uml/sequence_diagram.puml
    :caption: UML sequence diagram showing example operation.
    :align: center
    :width: 100%
