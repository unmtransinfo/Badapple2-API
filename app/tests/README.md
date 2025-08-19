# Tests

This directory contains tests written with `pytest` to check the validity of the app.

## Usage

1. Make sure you are in the `/app` folder
1. Setup and activate the project's virtual environment. For example, with conda use:
   ```
   conda create -n badapple2-api python=3.12 && conda activate badapple2-api
   ```
1. Run the tests:
   ```
   python -m pytest
   ```

## Acknowledgment

Test structure is based on:
https://testdriven.io/blog/flask-pytest/
