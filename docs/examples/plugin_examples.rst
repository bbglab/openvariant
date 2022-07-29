.. _Plugin examples:

Plugin examples
===============================

**OpenVariant** offers a plugin system, where the user will be able to build their own plugins and make a customized
data transformation. First of all, you will need to create a plugin; hence, check :ref:`Command-line interface` section
and :ref:`Command-line interface examples` to understand how a plugin template can be generated. Also, it is important
to know how plugins works and how they are composed in order to understand the following examples that we introduce.

We are going to introduce you two little plugins that we will use them in the example. The two plugins are described and built as:

*Add date* plugin
########################

It will generate a new field and it will add the today's date. `run` function will be executed for each line of the
*input* file, adding this new field. We can see on the following block the different codes that we add to obtain this.

On the *annotation* file we described the field that we want to add on the *output* file.

.. code-block:: yaml

  - type: plugin
    plugin: add_date
    field: DATE

In addition, after generating the plugin template with the command-line, we overwrite the `Add_dateContext` class and
`Add_datePlugin` class, in order to add the today's date on one field of the output.

.. code-block:: python

    from datetime import date

    from openvariant.plugins.context import Context
    from openvariant.plugins.plugin import Plugin

    # Context subclass
    class Add_dateContext(Context):

    	def __init__(self, row: dict, field_name: str, file_path: str) -> None:
    		super().__init__(row, field_name, file_path)

    # Plugin subclass
    class Add_datePlugin(Plugin):

    	def run(self, context: Add_dateContext) -> dict:
    		context.row[context.field_name] = str(date.today())

    		return context.row[context.field_name]

*Get length* plugin
########################

On this second plugin, we will get the length between two different numbers that are annotated as fields. For each row
of the *input* file, `run` function will be executed. It will get on the `START` field and `END` field and then it will get the length
between these two values (the difference).

In the  *annotation* file we find the following fields described as:

.. code-block:: yaml

  - type: plugin
    plugin: get_length
    field: LENGTH
  - type: internal
    field: START
    fieldSource:
      - 'loc.start'
  - type: internal
    field: END
    fieldSource:
      - 'loc.end'

Also, like in the previous plugin, we generated the plugin templated with command-line and then we overwrite them to
extract the length between the two fields.

.. code-block:: python

    from openvariant.plugins.context import Context
    from openvariant.plugins.plugin import Plugin

    # Context subclass
    class Get_lengthContext(Context):

    	def __init__(self, row: dict, field_name: str, file_path: str) -> None:
    		super().__init__(row, field_name, file_path)

    # Plugin subclass
    class Get_lengthPlugin(Plugin):

    	def run(self, context: Get_lengthContext) -> dict:
    		context.row[context.field_name] = str(int(context.row['END']) - int(context.row['START']))

    		return context.row[context.field_name]

These two plugins are used in the following example:

.. nbgallery::
    :name: Plugin System examples
    :glob:

    plugin_system/plugin_system.ipynb

We can find all the examples on the repository: `OpenVariant examples <https://github.com/bbglab/openvariant/tree/master/examples>`_.