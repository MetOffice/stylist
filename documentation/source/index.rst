Stylist Documentation
=====================

This documentation is split into two broad categories.

The user documentation is intended for people who wish to use Stylist as a
tool. Meanwhile the developer documentation is intended for those who wish to
extend and enhance it.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user-manual/index
   developer-information/index

The wiki associated with the project is used for more discursive material such
as design discussions. It is also an appropriate venue for technical
information of very limited interest, such as release process.

Concepts
~~~~~~~~

There are two concepts important to Stylist's function: Rules and Styles.

A rule is a single check which may be made against a piece of source code.
e.g. Has the implicit keyword been specified in all appropriate places?

A style, on the other hand, is a set of rules of interest to a particular
group of developers. For instance the LFRic style includes the "missing
implicit" rule and the "trailing white space rule."
