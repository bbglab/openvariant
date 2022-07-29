.. _Installation:

*********************
Installation
*********************

**OpenVariant** requires Python 3.9 or higher. In case you do not already have a Python environment configured on your computer,
check `Python Setup and Usage <https://docs.python.org/3/using/index.html>`_ from Python documentation to install and configure it.

Assuming that you have a default Python environment already configured, if you wish, you can also create and work with
Python virtual environments, follow instructions on `venv <https://docs.python.org/3/library/venv.html>`_  for further details.
Also, it is possible to create and work with a package manager like `Conda <https://github.com/conda/conda>`_ or `Mamba <https://github.com/mamba-org/mamba>`_.

Before installing **OpenVariant** you have to make sure that you have ``pip`` installed and updated with the last version.
Otherwise, follow the steps on `pip documentation <https://pip.pypa.io/en/stable/installation/>`_.


Install and update
===============================


To install **OpenVariant**, simply run this simple command in your terminal:

.. code-block:: bash

    pip install open-variant


To upgrade the package to the latest version use:

.. code-block:: bash

    pip install --upgrade open-variant

For further details visit our `PyPI package site <https://pypi.org/project/open-variant/>`_.

Install from source
=============================

**OpenVariant** is an open source project located on GitHub where is actively modified and developed. Can be installed
cloning the repository and installing from the source code as it follows:

.. code-block:: bash

    git clone git@github.com:bbglab/openvariant.git
    cd openvariant
    pip install -e .
