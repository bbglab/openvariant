from typing import Tuple

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
    """
    Removes the bases that are repeated in both ref and alt and are therefore NOT variants
    """
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


class Alteration_typePlugin(Plugin):
    """
    This plugin identifies the alteration type.
    Classifies the alteration type: checking POSITION, REF and ALT fields.
    The result will be store in a field of the input.
    """

    def run(self, row: dict):
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

            row['ALT_TYPE'] = alt_type
        else:
            raise ValueError("Unable to find 'REF', 'ALT' or 'POSITION' values in the row.")
        return row
