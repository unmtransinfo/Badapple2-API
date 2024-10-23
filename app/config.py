# config.py
from os import environ

# App
APP_NAME = environ.get("APP_NAME")
APP_PORT = environ.get("APP_PORT")
APP_URL = environ.get("APP_URL") or "localhost"

# Database
DB_HOST = environ.get("DB_HOST")
DB_NAME = environ.get("DB_NAME")
DB_USER = environ.get("DB_USER")
DB_PASSWORD = environ.get("DB_PASSWORD")
DB_PORT = int(environ.get("DB_PORT"))
