"""
@author Jack Ringer
Date: 8/19/2025
Description:
Creating fixtures to run tests on the app.
Based on: https://flask.palletsprojects.com/en/stable/testing/
"""

import pytest
from dotenv import load_dotenv

# Load test environment before importing app
load_dotenv(".env.test")

from app import app

app.config["TESTING"] = True


@pytest.fixture(scope="module")
def test_client():
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client
