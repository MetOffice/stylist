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
for your project. This is a simple Windows ``.ini`` format file. At a minimum
it should define a style of at least one rule.

For example, create a file called ``stylist.ini`` containing::

    [style.simple]
    rules = MissingImplicit

You may then check your source code using this style with::

    stylist -configuration stylist.ini <path to source>

The tool will alert you to any place where a program unit has been declared
without an ``implicit`` statement.

The "rules" field is a comma separated list so to add a second rule just append
``, MissingIntent``. Running the tool again will now warn you of both missing
Implicit statements and procedure arguments without ``intent`` properties.

You may define as many styles as you like in the configuration file. Lets add
a second to our example. Just add the following at the end::

    [style.extra]
    rules = FortranCharacterset

If the tool is given no guidance it will always choose the first style in the
configuration. If you want to use a different style (or be explicit) you can
use::

    stylist -configuration stylist.ini -style extra <path to source>

Some rules take arguments. Lets get bossy about the names which can be used
for type kinds. To the "extra" rules add
``, KindPattern(integer=r'i_.*', real=r'r_.*')``. This requires that all
integer kinds start with "i\_" and all real kinds start with "r\_".
