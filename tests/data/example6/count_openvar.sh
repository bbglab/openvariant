#!/bin/bash

# Usage:
# ./count_openvar.sh [cores to use]

CORES=$1

#source activate intogen2017

openvar count . -q --cores $CORES -g DATASET > count_variants_openvar.txt
openvar count . -q --cores $CORES -g DATASET -w ALT_TYPE=="snp" > count_variants_snp_openvar.txt
openvar count . -q --cores $CORES -g DATASET -w ALT_TYPE=="indel" > count_variants_indel_openvar.txt

# Count samples
openvar groupby . -q --cores $CORES -s "cut -f1 | uniq | sort -u | wc -l" -g DATASET | awk '{print($2" "$1)}' | sort -n > count_samples.txt
