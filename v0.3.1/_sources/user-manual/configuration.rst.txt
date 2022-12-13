Styles
======

Styles are defined in a configuration file by :py:class:`stylist.style.Style`
objects.

Extending an Existing  Style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a new rule to an existing style just add an instance of the rule class
to the constructor argument list. You may need to modify the ``import``
statements to make it available for use.

For instance:

.. code-block:: diff

   from stylist.fortran import (FortranCharacterset,
  -                             MissingImplicit)
  +                             MissingImplicit,
  +                             MissingOnly)
   from stylist.rule import TrailingWhitespace
   from stylist.style import Style

   lfric = Style(
                 FortranCharacterset(),
                 TrailingWhitespace(),
  -              MissingImplicit()
  +              MissingImplicit(),
  +              MissingOnly(ignore=['pfunit_mod', 'xios'])
                )

Adding a New Style
~~~~~~~~~~~~~~~~~~

As intimated above, this a simple matter of creating a new style object
variable.

.. code-block:: diff

   from stylist.fortran import (FortranCharacterset,
                                MissingImplicit,
                                MissingOnly)
   from stylist.rule import TrailingWhitespace
   from stylist.style import Style

   lfric = Style(
                 FortranCharacterset(),
                 TrailingWhitespace(),
                 MissingImplicit(),
                 MissingOnly(ignore=['pfunit_mod', 'xios'])
                )

  +special = Style(FortranCharacterset(),
  +                TrailingWhitespace(),
  +                MissingImplicit())
