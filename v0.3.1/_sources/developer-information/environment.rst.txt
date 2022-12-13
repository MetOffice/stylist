Create a Development Environment
================================

There are a number of different ways to create a suitable environment for
Stylist development. A few are documented here.

Whichever method you choose you will need to install certain packages. The
ultimate arbiter of what is needed is the ``setup.cfg`` file.

You will definitely need ``fparser`` and will probably want ``pytest``,
``flake8`` and ``mypy``.

Using a Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python supports cloning itself into stand alone instances at only the cost of
all your disc space. Creating one of these instances is as easy as::

    python3 -m venv ~me/place/which/i/like

This can be performed using any version of Python you may have temporarily
enabled using, for instance, environment modules. After the new virtual
instance is created those modules should be unloaded to avoid potential
confusion.

Once created a virtual instance is "activated"::

    source ~me/place/which/i/like/bin/activate

This sets everything up and modifies your command-line prompt to give a
reminder of which environment you are using. Once you are finished you can
get rid of it all with::

    deactivate

Populating the Environment
--------------------------

With the virtual instance active you can use the "pip" tool to install
anything you like from "pypi". These new libraries will not interact with
any installed in any other virtual environments you may have created.

e.g. ``python3 -m pip install pytest``
