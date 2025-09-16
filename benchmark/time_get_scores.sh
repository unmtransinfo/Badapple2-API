#!/bin/bash

# author: Jack Ringer
# Date: 9/16/2025
# Description: Simple script to record the time it takes to process all the scaffolds and their pScores from a given input file using the API
in_file="data/chembl_smiles.csv"
smiles_col=1
name_col=0
output_tsv="data/chembl_output.tsv"
local_port=8001
batch_size=500
idelim=","
cmd="python ../example_scripts/get_compound_scores.py --input_dsv_file ${in_file} --iheader --idelim ${idelim} --smiles_column ${smiles_col} --name_column ${name_col} --output_tsv ${output_tsv} --local_port ${local_port} --batch_size ${batch_size}"
time_ofile="time.txt"
(time $cmd) 2>&1 | tee $time_ofile
