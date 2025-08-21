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


def pytest_addoption(parser):
    """Introduce a flag for optional tests"""
    parser.addoption(
        "--run_activity",
        action="store_true",
        default=False,
        help="Run tests on API calls which use the 'activity' table",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_activity: mark test as requiring the 'activity' table in all DBs",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_activity"):
        # --run_activity given in cli: do not skip these tests
        return
    skip_activity = pytest.mark.skip(reason="need --run_activity option to run")
    for item in items:
        if "requires_activity" in item.keywords:
            item.add_marker(skip_activity)


@pytest.fixture(scope="session")
def flask_app():
    return app


@pytest.fixture(scope="module")
def url_prefix(flask_app):
    return flask_app.blueprints.get("version").url_prefix


@pytest.fixture(scope="module")
def test_client(flask_app):
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client
