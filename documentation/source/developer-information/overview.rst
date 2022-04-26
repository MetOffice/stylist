Overview
========

This overview is for all developers. It should give enough information to get 
started developing. It should also give reviewers a leg up on what to look for.


Unit Testing
------------

Unit testing is performed using the `pytest`_ tool. We look for high coverage,
the higher the better.

.. _pytest: https://docs.pytest.org/en/latest/


Type Hinting
------------

This project uses type hinting in order to catch some of those bone-headed
mistakes we all make. It should lead to long term more robust code. It also
furthers the goal of self documenting code by building type information into
the (semi-)runable code. That way it is less likely to get out of date.

We use the `mypy`_ tool to audit typing.

.. _mypy: http://www.mypy-lang.org/


Code Style
----------

As with most Python projects we follow the "PEP8" guidelines. The `flake8`_ tool is used for testing.

The general expectation is that source will pass the tests without incident. It
is recognised, however, that general guidelines can not always be applied to
specific requirements. As such we allow rules to be disabled providing the
reason is well understood and the scope of the exception is tightly drawn.

.. _flake8: https://github.com/pycqa/flake8


Documentation
-------------

Documentation is primarily managed with the `sphinx`_ tool.

We prefer API documentation to be automatically generated and wherever possible
from the code. That way it can't get out of sink with the code. For instance
we generate argument type information from type hints rather than hand written
entries in doc-strings.

This does not mean there is no place for hand-written documentation. It is
reserved for those matters which the source code cannot illuminate. The purpose
and reason for the code.

To build the documentation change into the ``documentation`` directory and use
``make html``. The resulting documents will be appear in ``build/html``.

.. _sphinx: https://www.sphinx-doc.org/en/master/
