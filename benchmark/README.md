# Benchmark

**TLDR**: The `compound_search/get_associated_scaffolds_ordered` endpoint can process ~120 compounds/second on a laptop computer without parallelization. YMMV depending on your system specs, how you setup gunicorn (`n_workers`) + use of parallelization, as well as your input dataset (compounds with more ring systems take more time to process).

This directory contains info on API benchmarks. It currently contains a simple script for recording the time it takes to process a list of compounds from a CSV file using the `compound_search/get_associated_scaffolds_ordered` endpoint.

## Usage

The steps below can be used to benchmark the `compound_search/get_associated_scaffolds_ordered` endpoint (i.e., computing scaffolds and fetching their information from the database for a given list of compounds).

1. Create/activate the `badapple2-api` environment by following [these instructions](../docs/README.md#python-environment-setup)
2. Modify [time_get_scores.sh](time_get_scores.sh) to match your requirements
   - If you want to benchmark against the ChEMBL dataset, you'll want to decompress the input file: `gzip -d data/chembl_smiles.gz`
3. Run: `bash time_get_scores.sh`

## Results

To approximate the speed of the `compound_search/get_associated_scaffolds_ordered` endpoint, a locally-installed version of the API was used to process the entire set of 2,474,590 compounds in the ChEMBL database (version 35) by running the [time_get_scores.sh](time_get_scores.sh) script.

The test was performed on a LG gram 17 laptop running Linux Mint 22.2 with the following specs (see [results/sysinfo.txt](results/sysinfo.txt) ):

```
CPU: 13th Gen Intel(R) Core(TM) i7-1360P
Cores: 16
Memory: 31.033 GB
```

The API was used to processes the 2,474,590 ChEMBL compounds with a single worker (no parallelization). The total time to process the compounds was `345m52.651s` (see [results/time.txt](results/time.txt)). Thus the API processed (approximately) 120 compounds per second on average.
