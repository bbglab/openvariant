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

def parse_hgvs_unknow(hgvs_str):
    return None

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
   
    result = prefix_map.get(prefix, ("Unknown", parse_hgvs_unknow, parse_hgvs_unknow))
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
