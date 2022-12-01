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

This project uses type hinting in order to catch some of those stupid mistakes
we all make from time to time. It should lead to more robust code in the long
term. It also furthers the goal of self documenting code by building type
information into the runnable code. That way it is less likely to get out of
date.

We use the `mypy`_ tool to audit typing.

.. _mypy: http://www.mypy-lang.org/


Code Style
----------

As with most Python projects we follow the "PEP8" guidelines. The `flake8`_
tool is used for testing.

The general expectation is that source will pass the tests without incident. It
is recognised, however, that general guidelines can not always be applied to
specific requirements. As such we allow rules to be disabled providing the
reason is well understood and the scope of the exception is tightly drawn.

.. _flake8: https://github.com/pycqa/flake8


Documentation
-------------

Documentation is primarily managed with the `sphinx`_ tool.

We prefer API documentation to be automatically generated and wherever possible
from the code. That way it can't get out of sync with that code. For instance
we generate argument type information from type hints rather than hand written
entries in docstrings.

This does not mean there is no place for hand-written documentation. It is
reserved for those matters which the source code cannot illuminate: The purpose
and reason for the code.

To build the documentation change into the ``documentation`` directory and use
``make html``. The resulting documents will be appear in ``build/html``.

.. _sphinx: https://www.sphinx-doc.org/en/master/

Docstrings
..........

Following PEP8 guidance Docstrings are expected for every scoping unit. There
is an exception for class constructors which take no arguments. The
constructor inherits its summary from the class, only the arguments need to be
documented.

Try to avoid unnecessary verbiage. If you are documenting a class there is no
need to mention that the thing being documented is a class. For example,
rather than "class representing a thing" it is sufficient to say "A thing."

Also try to avoid repeating what is already in the source. If a function is
called "multiply" and takes two arguments don't document it with "Multiplies
two numbers." Instead talk about things which are not captured in the source,
for instance there might be units associated with arguments.

Remember that type hinting is used in synthesising the API documentation so
there is no need to repeat that. When documenting arguments do say
"Temperature in Kelvin." Don't say "Floating point Kelvin."

Docstrings should be used for information not expressed in the code. This can
be challenging as well chosen function and argument names make the code
largely self documenting.

You may also assume the reader understands the basics of the language. For
example there's little value to documenting a class constructor with
"Constructor to create an object." We all know it's a constructor and that's
what they do. Instead try to say something about the arguments passed.
Although constructors are a special case, see previously.

Todo items
..........

Generally future work should be raised as issues in the project database.

There will be situations where a piece of future work (or potential future
work) needs to be recorded but doesn't form a coherent issue. In these cases
a "todo" block in the docstring may be appropriate

