# config.py
from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

# App
APP_NAME = environ.get("APP_NAME")
APP_PORT = environ.get("APP_PORT")
APP_URL = environ.get("APP_URL") or "localhost"
URL_PREFIX = environ.get("URL_PREFIX") or ""

# Database
databases = [
    {
        "name": environ.get("DB_NAME"),
        "host": environ.get("DB_HOST"),
        "user": environ.get("DB_USER"),
        "password": environ.get("DB_PASSWORD"),
        "port": int(environ.get("DB_PORT")),
    },
    {
        "name": environ.get("DB2_NAME"),
        "host": environ.get("DB2_HOST"),
        "user": environ.get("DB2_USER"),
        "password": environ.get("DB2_PASSWORD"),
        "port": int(environ.get("DB2_PORT")),
    },
]

DB_NAME2HOST = {}
DB_NAME2USER = {}
DB_NAME2PASSWORD = {}
DB_NAME2PORT = {}
ALLOWED_DB_NAMES = []  # note: set is not JSON-serializable
for db in databases:
    DB_NAME2HOST[db["name"]] = db["host"]
    DB_NAME2USER[db["name"]] = db["user"]
    DB_NAME2PASSWORD[db["name"]] = db["password"]
    DB_NAME2PORT[db["name"]] = db["port"]
    ALLOWED_DB_NAMES.append(db["name"])


# API limits
# limits on max rings
# TODO: make this match api_spec.yml
MAX_RING_LOWER_BOUND = 1
MAX_RING_UPPER_BOUND = 10

# Only include this page description if in prod
PROD_ONLY_ADDL_DESCRIPTION = """
\n\n
Note: This API is intended for moderate use cases and does not include all the functions available on the locally hosted version (e.g., searching for specific assay outcomes). 
    One can setup the API locally by following the instructions here: https://github.com/unmtransinfo/Badapple2-API/blob/main/README.md#setup-development
"""

# these API calls are only available on localhost
# (are computationally expensive and/or require activity table)
DEV_ONLY_PATHS = [
    "/scaffold_search/get_associated_assay_ids",
    "/substance_search/get_assay_outcomes",
]
