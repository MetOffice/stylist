Installing Stylist
------------------

The easiest way to install the tool is using PIP and `PyPI`_. To install it for
your own use you might try ``pip install --user stylist``. You may prefer to
install it to one or more virtual environments using ``pip install stylist``
which will also allow a system administrator to install it for all users on a
system.

If you prefer to manage software using Anaconda then it is also available
through `CondaForge`_. Use ``conda install -c conda-forge stylist``.

.. _PyPI: https://pypi.org/project/stylist/
.. _CondaForge: https://anaconda.org/conda-forge/stylist

Getting started
---------------

With the tool installed and available you will need to create a configuration
for your project. This is a simple Python script which defines suitable
variables. At a minimum it should define a style of at least one rule.

For example, create a file called ``stylist.py`` containing::

    from stylist.fortran import MissingImplicit
    from stylist.style import Style

    simple = Style(MissingImplicit())

You may then check your source code using this style with::

    stylist -configuration stylist.py <path to source>

The tool will alert you to any place where a program unit has been declared
without an ``implicit`` statement.

The Style object is constructed with all the rules which make up that style.
To add a second rule just import it and append ``, MissingIntent()`` to the
argument list::

    from stylist.fortran import MissingImplicit, MissingIntent
    from stylist.style import Style

    simple = Style(MissingImplicit(), MissingIntent())

Running the tool again will now warn you of both missing ``implicit``
statements and procedure arguments without ``intent`` properties.

You may define as many styles as you like in the configuration file. Lets add
a second to our example. Just extend the import and add the following at the
end::

    extra = Style(FortranCharacterset())

If the tool is given no guidance it will always choose the first style in the
configuration. If you want to use a different style (or be explicit) you can
use::

    stylist -configuration stylist.py -style extra <path to source>

Some rules take arguments. Let's get bossy about the names which can be used
for type kinds::

    from re import compile as recompile
    from stylist.rule import (MissingImplicit,
                              MissingIntent,
                              FortranCharacterset,
                              KindPattern)
    from stylist.style import Style

    simple = Style(MissingImplicit(), MissingIntent())

    extra = Style(FortranCharacterset(),
                  KindPattern(integer=recompile(r'i_.*'),
                              real=recompile(r'r_.*')))

This requires that all integer kinds start with "i\_" and all real kinds
start with "r\_".
