# Example Scripts

This directory contains example scripts which make use of the Badapple2 API.

## Script Usage

### `get_compound_scores.py`

This script processes an input CSV/TSV file containing compound structures and outputs information on all of the scaffolds linked to these compounds in the Badapple database.

Example usage:

```
python get_compound_scores.py --input_dsv_file data/example_input.tsv --iheader --smiles_column 1 --name_column 0 --output_tsv data/example_output.tsv --local_port 8000 --batch_size 20
```

Output of `python get_compound_scores.py -h`:

```
usage: get_compound_scores.py [-h] --input_dsv_file
                              INPUT_DSV_FILE [--idelim IDELIM]
                              [--iheader]
                              [--smiles_column SMILES_COLUMN]
                              [--name_column NAME_COLUMN]
                              --output_tsv OUTPUT_TSV
                              [--max_rings MAX_RINGS]
                              [--batch_size BATCH_SIZE]
                              [--database DATABASE]
                              [--local_port LOCAL_PORT]

Get scaffold pScores and other info for input compound SMILES
from a TSV file.

options:
  -h, --help            show this help message and exit
  --input_dsv_file INPUT_DSV_FILE
                        Delimiter-separated file (e.g., CSV)
                        which contains molecule names and SMILES
  --idelim IDELIM       Delimiter for input DSV file (default is
                        tab)
  --iheader             Input DSV file has header line
  --smiles_column SMILES_COLUMN
                        (integer) column where SMILES are
                        located (for input DSV file)
  --name_column NAME_COLUMN
                        (integer) column where molecule names
                        are located (for input DSV file). Names
                        should be unique!
  --output_tsv OUTPUT_TSV
                        Output TSV file, will include all info
                        from input DSV as well as Badapple info
                        (scafID, pScore, inDrug, etc)
  --max_rings MAX_RINGS
                        Maximum number of ring systems allowed
                        in input compounds. Compounds with >
                        max_rings will not be processed. Note
                        that the API will hard cap you at 10.
  --batch_size BATCH_SIZE
                        Number of compounds to fetch scaffold
                        details on with each request. Note that
                        the API will hard cap you at 1000,
                        recommended to be <=100
  --database DATABASE   Badapple database to fetch info from
  --local_port LOCAL_PORT
                        (Localhost only) API port. Provide only
                        if you have setup and would like to use
                        the local version of Badapple2-API.
```
