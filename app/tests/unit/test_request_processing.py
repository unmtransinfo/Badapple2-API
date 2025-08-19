"""
@author Jack Ringer
Date: 8/19/2025
Description:
Tests for functions in request_processing.py
"""

import pytest
from flask import request
from utils.request_processing import (
    get_database,
    int_check,
    process_integer_list_input,
    process_list_input,
)
from werkzeug.exceptions import BadRequest

# --------- int_check -------------


def test_valid_int(flask_app):
    with flask_app.test_request_context("/?n=5"):
        result = int_check(request, "n", lower_limit=1, upper_limit=10)
        assert result == 5


def test_missing_value_uses_default(flask_app):
    with flask_app.test_request_context("/"):
        result = int_check(request, "n", default_val=7)
        assert result == 7


def test_below_lower_limit(flask_app):
    with flask_app.test_request_context("/?n=0"):
        with pytest.raises(BadRequest) as exc:
            int_check(request, "n", lower_limit=1)
        assert "must be greater" in str(exc.value)


def test_above_upper_limit(flask_app):
    with flask_app.test_request_context("/?n=100"):
        with pytest.raises(BadRequest) as exc:
            int_check(request, "n", upper_limit=50)
        assert "must be less" in str(exc.value)


def test_invalid_type(flask_app):
    with flask_app.test_request_context("/?n=foo"):
        with pytest.raises(BadRequest) as exc:
            int_check(request, "n")
        assert "Expected int" in str(exc.value)


def test_zero(flask_app):
    with flask_app.test_request_context("/?n=0"):
        result = int_check(request, "n", lower_limit=-10, upper_limit=10)
        assert result == 0


# ---------- get_database ----------
# NOTE: assuming here that .env.test includes "badapple_classic" and "badapple2"


def test_get_database_valid(flask_app):
    with flask_app.test_request_context("/?database=badapple_classic"):
        result = get_database(request)
        assert result == "badapple_classic"


def test_get_database_default(flask_app):
    with flask_app.test_request_context("/"):
        result = get_database(request, default_val="badapple2")
        assert result == "badapple2"


def test_get_database_invalid(flask_app):
    with flask_app.test_request_context("/?database=not_a_real_db"):
        with pytest.raises(BadRequest) as exc:
            get_database(request)
        assert "Invalid database" in str(exc.value)


# ---------- process_list_input ----------


def test_process_list_input_valid(flask_app):
    with flask_app.test_request_context("/?ids=1,2,3"):
        result = process_list_input(request, "ids", limit=5)
        assert result == ["1", "2", "3"]


def test_process_list_input_missing(flask_app):
    with flask_app.test_request_context("/"):
        with pytest.raises(BadRequest) as exc:
            process_list_input(request, "ids", limit=5)
        assert "No ids provided" in str(exc.value)


def test_process_list_input_exceeds_limit(flask_app):
    with flask_app.test_request_context("/?ids=1,2,3,4,5,6"):
        with pytest.raises(BadRequest) as exc:
            process_list_input(request, "ids", limit=5)
        assert "exceeded limit" in str(exc.value)


# ---------- process_integer_list_input ----------


def test_process_integer_list_input_valid(flask_app):
    with flask_app.test_request_context("/?ids=1,2,3"):
        result = process_integer_list_input(request, "ids", limit=5)
        assert result == [1, 2, 3]


def test_process_integer_list_input_non_integer(flask_app):
    with flask_app.test_request_context("/?ids=1,two,3"):
        with pytest.raises(BadRequest) as exc:
            process_integer_list_input(request, "ids", limit=5)
        assert "contains non-integer elements" in str(exc.value)
