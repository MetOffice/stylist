# Stylist

The immediate need was for a code style checking tool which understood Fortran.
Such things being quite thin on the ground. However very few large software
projects are implemented in a single language. Thus a tool was developed which
provided a framework to aid in delivering support for multiple languages and
multiple style choices.

The framework supports multiple styles, each consisting of multiple rules.
Each of these may be one of two types, those which treat the source as a text
file and those which treat it as a parse tree.

The project is still in its infancy so only a few rules have been implemented
and only for fortran.

## Design

In the past we have used text based tools and there's a surprising amount you
can do with regular expressions. However once context becomes important they
can become a liability. In those cases it is much better to have the parse
tree.

At the moment the tool is only able to flag up where a style rule has been
broken. For some things this is the best we can hope for but for others
we might aspire to correct the problem.

For instance the current check for missing `implicit none` statements might,
in the future, insert them where they are missing.

Some UML class diagrams have been prepared which may be found in the
`documentation` directory. These make use of the
[PlantUML](https://plantuml.com) tool to render.
