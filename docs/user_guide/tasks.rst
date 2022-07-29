.. _Tasks:

Tasks
===============================

**OpenVariant** is a package that can perform different functionalities with multiple files as an input. In this section
we will describe the tasks that can be executed with this library. If you want a more practical demo or some possible use of cases,
check :ref:`Examples` section.

Find files
------------------------------

From a base path (directory or file) it will generate an iterator that will throw all the `input` files and its
corresponding `annotation` file that matches the ``pattern`` parameter.

This is can be useful to make sure which `annotation` file can correspond on each `input` file and then each file can
be parsed through `Variant <#id2>`_ task. Check :ref:`Find files examples` for more cases.

.. code-block:: python

    # Example
    from openvariant import find_files

    for file, annotation in find_files("datasets/"):
        print(f"File path: {file} - Annotation object: {annotation}")

Variant
------------------------------

Allow us to parse an `input` file through the `annotation` file. It will generate an object which you can apply different
functionalities. Here, there is an example, but for further details and more in-depth understanding of each functionality,
check :ref:`Variant examples`.

.. code-block:: python

    # Example
    from openvariant import Annotation, Variant

    file_path = "./indexes.tsv"
    annotation = Annotation("./metadata.yaml")
    result = Variant(file_path, annotation)
    for line in result.read():
        print(f"Line in a dict: {line}")


Cat
------------------------------

It will show on the stdout (standard out) the whole parsed output. This task can be also executed with :ref:`Command-line interface`.
Check, Cat examples in :ref:`Tasks examples` for more cases.

.. code-block:: python

    # Example
    from openvariant.tasks import cat

    file_path = "./indexes.tsv"
    annotation_path = "./metadata.yaml"

    cat(file_path, annotation_path)

Group by
------------------------------

It will generate an iterator that will throw three variables: ``group_key`` (the value of each group), ``group_result``
(a list of all rows that pertain to each group) and ``command`` (if it uses the `script` parameter or not).
It will group the parsed result for each different value of the specified ``key_by``. For further details, check out the
Group by examples in :ref:`Tasks examples`.

.. code-block:: python

    # Example
    from openvariant.tasks import group_by

    file_path = "./indexes.tsv"
    annotation_path = "./metadata.yaml"

    for group_key, group_result, command in group_by(file_path, annotation_path, script=None, key_by='COUNTRY'):
        for r in group_result:
            print(f"{group_key}\t{r}")

Count
------------------------------

It returns the number of rows that matches a specific conditions. You can see more examples in this section:
Count examples in :ref:`Tasks examples`.

.. code-block:: python

    # Example
    from openvariant.tasks import count

    file_path = "./indexes.tsv"
    annotation_path = "./metadata.yaml"

    result = count(file_path, annotation_path)
    print(result)
