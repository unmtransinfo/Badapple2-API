# Benchmark

This directory contains info on API benchmarks. It currently contains a simple script for recording the time it takes to process a list of compounds from a CSV file using the `compound_search/get_associated_scaffolds_ordered` endpoint.

## Usage

The steps below can be used to benchmark the `compound_search/get_associated_scaffolds_ordered` endpoint (i.e., computing scaffolds and fetching their information from the database for a given list of compounds).

1. Create/activate the `badapple2-api` environment by following [these instructions](../docs/README.md#python-environment-setup)
2. Modify [time_get_scores.sh](time_get_scores.sh) to match your requirements
3. Run: `bash time_get_scores.sh`
