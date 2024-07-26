.. _Command-line interface:

.. role:: bash(code)
  :language: bash
  :class: highlight

Command-line interface (CLI)
===============================

**OpenVariant** is a package that can be run in Python scripts, but, also, allow to the user to run some of its tasks
in a shell and command language. The same tasks that can be executed through a command-line interface (CLI) that we present
here can be also performed in a Python script.

The main command that rules **OpenVariant** is :bash:`openvar`, with that command we can choose different options to perform different tasks.
The tasks with their parameters are the following ones:

.. code:: bash

    $ openvar --help

    Usage: openvar [OPTIONS] COMMAND [ARGS]...

      'openvar' is the command-line interface of OpenVariant. Parsing and data
      transformation of multiple input formats.

    Options:
      --version   Show the version and exit.
      -h, --help  Show this message and exit.

    Commands:
      cat      Concatenate parsed files to standard output.
      count    Number of rows that matches a specified criterion.
      groupby  Group the parsed result for each different value of the specified key.
      plugin   Actions to execute for a plugin: create.

Cat command
############

Concatenate parsed files on the standard output. For these options the parameters are the following ones:

* ``input_path`` - Input path.
* ``-w,--where`` - Condition expression.
* ``-a,--annotations`` - Annotation path.
* ``--header`` - Show headers on the result.

.. code-block:: bash

    # Example
    openvar cat /project/datasets -w "SCORE >= 5" -a /project/annotation.yaml  --header


Count command
###############

Number of rows that matches a specific condition. The parameters are the following ones:

* ``input_path`` - Input path.
* ``-w,--where`` - Condition expression.
* ``-g,--group_by`` - Key to group rows.
* ``-a,--annotations`` - Annotation path.
* ``-c,--cores`` - Maximum processes to run in parallel.
* ``-q,--quite`` - Don't show the progress.

.. code-block:: bash

    # Example
    openvar count /project/datasets -w "REF >= 5034" -g COUNTRY -a /project/annotation.yaml -c 10 -q

Group by command
#################

Number of rows that matches a specific condition. The parameters are the following ones:

* ``input_path`` - Input path.
* ``-w,--where`` - Condition expression.
* ``-g,--group_by`` - Key to group rows.
* ``-a,--annotations`` - Annotation path.
* ``-c,--cores`` - Maximum processes to run in parallel.
* ``-q,--quite`` - Don't show the progress.

.. code-block:: bash

    # Example
    openvar count /project/datasets -w "REF >= 5034" -g COUNTRY -a /project/annotation.yaml -c 10 -q

Plugin command
################

Actions to apply on the plugins system. Mainly create the template of a new plugin. For that, these parameters can be used
(to learn more about how plugins work, check :ref:`Plugin system` section):

* ``action`` - Action to perform ['create'].
* ``-n,--name`` - Name of the plugin.
* ``-d,--directory`` - Directory path where plugin is or will be located.

Create
--------

It will generate the template with required files to apply and run a new plugin with the name stipulated and in the
default directory.

.. code-block:: bash

    # Example
    openvar plugin create -n reverse_value

For further details, check :ref:`Command-line interface examples` and you will have a clearer picture on how to use CLI tasks.