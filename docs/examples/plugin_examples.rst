.. _Plugin examples:

Plugin examples
===============================



**OpenVariant** offers a plugin system, where the user will be able to build their own plugins and make a customized
data transformation. First of all, you will need to create a plugin; hence, check :ref:`Command-line interface` section
and :ref:`Command-line interface examples` to understand how a plugin template can be generated. Also, it is important
to know how plugins works and how they are composed in order to understand the following examples that we introduce.

Unique field plugin
----------------------

Plugins can modify individual fields, and in this example, we introduce two small plugins that are described and
implemented as follows:

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

Multiple fields plugin
-------------------------

The plugin system allows transforming multiple fields simultaneously, and can be constructed as follows:

*HGVS decoder* plugin
#######################

`The Human Genome Variation Society (HGVS) Nomenclature <https://hgvs-nomenclature.org/stable/>`_ is the global standard
for describing DNA, RNA, and protein sequence variants. It is widely used in clinical reports, scientific publications,
and variant databases to communicate genetic changes. HGVS variants are expressed using a specific syntax that encodes
detailed information about the type and location of the change  (e.g `c.76A>T`, `r.76_78del`, `p.Gly76_Val78del`).

In this plugin, we decode HGVS expressions by identifying and separating the variant type (*TYPE*), its position (*POSITION*),
and the specific change that occurs (*VARIANT*).

The *annotation* file with multiple fields can be described as:

.. code-block:: yaml

    columns:
        - TYPE
        - POSITION
        - VARIANT

    annotation:
        - type: plugin
          plugin: multi_test
          field:
            - TYPE
            - POSITION
            - VARIANT
        - type: internal
          field: HGVS
          fieldSource:
            - 'HGVS Consequence'
            - HGVSp


We built the plugin with attention to the order of the different fields it processes.

.. code-block:: python

    from openvariant.plugins.context import Context
    from openvariant.plugins.plugin import Plugin

    import re

    class HGVS_decoderContext(Context):

        def __init__(self, row: dict, field_name: str, file_path: str) -> None:
            super().__init__(row, field_name, file_path)


    amino_acids_map = {
        "Ala": "Alanine",
        "Arg": "Arginine",
        "Asn": "Asparagine",
        "Asp": "Aspartic Acid",
        "Cys": "Cysteine",
        "Gln": "Glutamine",
        "Glu": "Glutamic Acid",
        "Gly": "Glycine",
        "His": "Histidine",
        "Ile": "Isoleucine",
        "Leu": "Leucine",
        "Lys": "Lysine",
        "Met": "Methionine",
        "Phe": "Phenylalanine",
        "Pro": "Proline",
        "Ser": "Serine",
        "Thr": "Threonine",
        "Trp": "Tryptophan",
        "Tyr": "Tyrosine",
        "Val": "Valine",
        "Ter": "Termination codon"
    }

    variant_map = {
        "delins": "deletion-insertion by ",
        "del": "deletion",
        "ins": "insertion of ",
        "dup": "duplication",
        "inv": "inversion",
        "con": "conversion",
        "ext": "extension of ",
        "fs": "frameshift mutation of "
    }

    position_regex = re.compile(r'(\(?\*?-?\??\_?\d+(?:\_?[+-]\d+\??)?\)?(_)?(?:\(?\*?-?\d+\_?(?:[+-]\d+)?\??\)?)?)')
    protein_position_regex = re.compile(r'(?<!\*)(?<!\-)(\d+)\=?\*?')

    nucleotides = re.compile(r'([ACTG]+|[agc]+[u]?)')
    variant_regex = re.compile(r'[ACTG]+>[ACTG]+|del|ins[ACTG]+|dup|inv|con|\[[0-9]+\]|delins[ACTG]+')
    variant_rna_regex = re.compile(r'[agcu]+>[agcu]+|del|ins[agcu]+|dup|inv|con|\[[0-9]+\]|delins[agcu]+')

    amino_acids = r'(?:Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val|Ter)'
    variant_protein_aa_regex = re.compile(rf'(?<!ext)(?<!fs)(?<!ins)(?<!delins){amino_acids}')
    variant_protein_mod_regex = re.compile(rf'(?:delins{amino_acids}|del|ins{amino_acids}|dup|inv|con|ext{amino_acids}?\*?(?:[0-9]+)?|fs{amino_acids}[0-9]+)')
    variant_type_regex = re.compile(f'(?:delins|del|ins|dup|inv|con|ext|fs)')

    def parse_hgvs_pos(hgvs_str):
        matches_pos = re.findall(position_regex, hgvs_str)
        position = [m[0] for m in matches_pos]
        position = ";".join(position)
        return position

    def parse_hgvs_pos_protein(hgvs_str):
        matches_pos = re.findall(protein_position_regex, hgvs_str)
        position = [m for m in matches_pos]
        position = ";".join(position)
        return position

    def parse_hgvs_variant(hgvs_str):
        matches = re.findall(variant_regex, hgvs_str)
        matches_variant = re.findall(variant_type_regex, matches[0])
        if len(matches_variant) > 0:
            variant = variant_map.get(matches_variant[0])
            matches_n = re.findall(nucleotides, matches[0])
            if len(matches_n) > 0:
                variant += matches_n[0]
        else:
            variant = matches[0]
        return variant

    def parse_hgvs_variant_protein(hgvs_str):
        matches = re.findall(variant_protein_aa_regex, hgvs_str)
        if len(matches) == 1:
            variant = amino_acids_map.get(matches[0])
        else:
            aa_1 = amino_acids_map.get(matches[0])
            aa_2 = amino_acids_map.get(matches[1])
            if aa_1 == aa_2:
                variant = "Synonymous (silent) variant"
            else:
                variant = aa_1 + " mutated to " + aa_2
        matches = re.findall(variant_protein_mod_regex, hgvs_str)
        if len(matches) > 0:
            variant += " and "
            matches_variant = re.findall(variant_type_regex, matches[0])
            variant += variant_map.get(matches_variant[0])
            matches_amino_acid = re.findall(amino_acids, matches[0])
            if len(matches_amino_acid) > 0:
                variant += amino_acids_map.get(matches_amino_acid[0])
        return variant

    def interpret_hgvs(hgvs_str):
        prefix_map = {
            "g.": ("gDNA", parse_hgvs_pos, parse_hgvs_variant),
            "c.": ("cDNA", parse_hgvs_pos, parse_hgvs_variant),
            "n.": ("ncDNA", parse_hgvs_pos, parse_hgvs_variant),
            "m.": ("mtDNA", parse_hgvs_pos, parse_hgvs_variant),
            "r.": ("RNA", parse_hgvs_pos, parse_hgvs_variant),
            "p.": ("Protein", parse_hgvs_pos_protein, parse_hgvs_variant_protein),
        }

        prefix = hgvs_str[:2]

        result = prefix_map.get(prefix, ("Unknown", [], []))
        seq = hgvs_str[2:]

        type_variant = result[0]
        position = result[1](seq)
        variant = result[2](seq)

        return type_variant, position, variant



    class HGVS_decoderPlugin(Plugin):

        def run(self, context: HGVS_decoderContext) -> dict:

            value = context.row["HGVS"]
            type_variant, position, variant = interpret_hgvs(value)

            return type_variant, position, variant



We can find all the examples on the repository: `OpenVariant examples <https://github.com/bbglab/openvariant/tree/master/examples>`_
and these plugins are used in the following examples:

.. nbgallery::
    :name: Plugin System examples
    :glob:

    plugin_system/plugin_system.ipynb

