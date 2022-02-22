from typing import Tuple

from openvariant.plugins.context import Context
from openvariant.plugins.plugin import Plugin


def _prefix_length(ref: str, alt: str) -> int:
    i = 0
    while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
        i += 1
    return i


def _suffix_length(ref: str, alt: str) -> int:
    i = len(ref) - 1
    j = len(alt) - 1
    while i >= 0 and j >= 0 and ref[i] == alt[j]:
        i -= 1
        j -= 1
    return len(ref) - i - 1


def _indel_postprocess(start: int, ref: str, alt: str) -> Tuple[str, str, str]:
    """Removes the bases that are repeated in both ref and alt and are therefore NOT variants"""
    prefix_len = _prefix_length(ref, alt)
    ins_correction = 1 if len(ref) < len(alt) else 0
    start = int(start) + max(0, prefix_len - ins_correction)
    alt = alt[prefix_len:]
    ref = ref[prefix_len:]

    suffix_len = _suffix_length(ref, alt)
    if suffix_len > 0:
        alt = alt[:-suffix_len]
        ref = ref[:-suffix_len]

    ref = '-' if ref == '' else ref
    alt = '-' if alt == '' else alt

    return str(start), str(ref), str(alt)


class Alteration_typeContext(Context):
    """
    The context of this plugin will be the simplest one, without any added property or methods.

    Attributes
    ----------
    row : dict
        The row that data transformation will be applied.
    field_name : str
        Name of the corresponding column that was described on the annotation schema.
    file_path : str
        Path of the Input file that is being parsed.
    """

    def __init__(self, row: dict, field_name: str, file_path: str) -> None:
        super().__init__(row, field_name, file_path)


class Alteration_typePlugin(Plugin):
    """
    This plugin identifies the alteration type.
    Classifies the alteration type: checking POSITION, REF and ALT fields.
    The result will be store in a field of the input.
    """

    def run(self, context: Alteration_typeContext) -> str:
        """Extract alteration type from the input row.

        Parameters
        ----------
        context : Alteration_typeContext
            Representation of the row to be parsed.

        Returns
        -------
        str
            The value of ALT_TYPE field.
        """
        row = context.row
        if 'REF' in row and 'ALT' in row:
            l_ref = len(row['REF'])
            l_alt = len(row['ALT'])

            if l_alt != l_ref:
                alt_type = "indel"
            else:
                if l_alt > 1:
                    alt_type = "mnv"
                else:
                    if '-' in row['REF'] or '-' in row['ALT']:
                        alt_type = "indel"
                    else:
                        alt_type = "snv"
            if alt_type == "indel":
                row['POSITION'], row['REF'], row['ALT'] = _indel_postprocess(row['POSITION'], row['REF'], row['ALT'])

            row[context.field_name] = alt_type
        else:
            raise ValueError("Unable to find 'REF', 'ALT' or 'POSITION' values in the row.")
        return row[context.field_name]
