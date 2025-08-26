# Tests

This directory contains tests written with `pytest` to check the validity of the app.

## Usage

1. Make sure you are in the `/app` folder: `cd app/`
2. Create a test environment (modify as needed):

   ```
   cp .env.example .env.test
   ```

3. Setup and activate the project's virtual environment by following the instructions [here](../../docs/README.md#python-environment-setup)
4. Run the tests:

   ```
   python -m pytest
   ```

   If you want to include all tests (i.e., including those that require the `activity` table):

   ```
   python -m pytest --requires_activity
   ```

## Acknowledgment

Test structure is based on:
https://testdriven.io/blog/flask-pytest/
