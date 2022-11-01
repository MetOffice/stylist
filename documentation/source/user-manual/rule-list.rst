Available Rules
===============

You are now ready to get started developing your own styles. All you need now
are a list of the available rules.

.. Comment: it would be nice to auto generate these lists.

Language-agnostic Rules
-----------------------

Some rules are widely applicable regardless of source language.

.. autoclass:: stylist.rule.TrailingWhitespace
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine

Fortran Rules
-------------

Rules relating to Fortran source code.

.. autoclass:: stylist.fortran.AutoCharArrayIntent
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.ForbidUsage
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.FortranCharacterset
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.IntrinsicModule
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.KindPattern
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.LabelledDoExit
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.MissingImplicit
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.MissingIntent
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.MissingOnly
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.MissingPointerInit
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran

.. autoclass:: stylist.fortran.NakedLiteral
   :noindex:
   :no-show-inheritance:
   :exclude-members: examine, examine_fortran
