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
    param_given,
    process_integer_list_input,
    process_list_input,
)
from werkzeug.exceptions import BadRequest


class TestParamGiven:
    def test_param_present(self, flask_app):
        with flask_app.test_request_context("/?n=100"):
            assert param_given(request, "n")

    def test_param_not_present(self, flask_app):
        with flask_app.test_request_context("/"):
            assert param_given(request, "n") == False

    def test_param_present_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": 100}):
            assert param_given(request, "n")

    def test_param_not_present_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={}):
            assert param_given(request, "n") == False


class TestIntCheck:
    def test_valid_int(self, flask_app):
        with flask_app.test_request_context("/?n=5"):
            result = int_check(request, "n", lower_limit=1, upper_limit=10)
            assert result == 5

    def test_valid_int_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": 5}):
            result = int_check(request, "n", lower_limit=1, upper_limit=10)
            assert result == 5

    def test_missing_value_uses_default(self, flask_app):
        with flask_app.test_request_context("/"):
            result = int_check(request, "n", default_val=7)
            assert result == 7

    def test_missing_value_uses_default_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={}):
            result = int_check(request, "n", default_val=7)
            assert result == 7

    def test_below_lower_limit(self, flask_app):
        with flask_app.test_request_context("/?n=0"):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n", lower_limit=1)
            assert "must be greater" in str(exc.value)

    def test_below_lower_limit_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": 0}):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n", lower_limit=1)
            assert "must be greater" in str(exc.value)

    def test_above_upper_limit(self, flask_app):
        with flask_app.test_request_context("/?n=100"):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n", upper_limit=50)
            assert "must be less" in str(exc.value)

    def test_above_upper_limit_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": 100}):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n", upper_limit=50)
            assert "must be less" in str(exc.value)

    def test_invalid_type(self, flask_app):
        with flask_app.test_request_context("/?n=foo"):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n")
            assert "Expected int" in str(exc.value)

    def test_invalid_type_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": "foo"}):
            with pytest.raises(BadRequest) as exc:
                int_check(request, "n")
            assert "Expected int" in str(exc.value)

    def test_zero(self, flask_app):
        with flask_app.test_request_context("/?n=0"):
            result = int_check(request, "n", lower_limit=-10, upper_limit=10)
            assert result == 0

    def test_zero_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={"n": 0}):
            result = int_check(request, "n", lower_limit=-10, upper_limit=10)
            assert result == 0


# NOTE: assuming here that .env.test includes "badapple_classic" and "badapple2"


class TestGetDatabase:
    def test_get_database_valid(self, flask_app):
        with flask_app.test_request_context("/?database=badapple_classic"):
            result = get_database(request)
            assert result == "badapple_classic"

    def test_get_database_valid_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"database": "badapple_classic"}
        ):
            result = get_database(request)
            assert result == "badapple_classic"

    def test_get_database_default(self, flask_app):
        with flask_app.test_request_context("/"):
            result = get_database(request, default_val="badapple2")
            assert result == "badapple2"

    def test_get_database_default_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={}):
            result = get_database(request, default_val="badapple2")
            assert result == "badapple2"

    def test_get_database_invalid(self, flask_app):
        with flask_app.test_request_context("/?database=not_a_real_db"):
            with pytest.raises(BadRequest) as exc:
                get_database(request)
            assert "Invalid database" in str(exc.value)

    def test_get_database_invalid_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"database": "not_a_real_db"}
        ):
            with pytest.raises(BadRequest) as exc:
                get_database(request)
            assert "Invalid database" in str(exc.value)


class TestProcessListInput:
    def test_process_list_input_valid(self, flask_app):
        with flask_app.test_request_context("/?ids=1,2,3"):
            result = process_list_input(request, "ids", limit=5)
            assert result == ["1", "2", "3"]

    def test_process_list_input_valid_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": ["1", "2", "3"]}
        ):
            result = process_list_input(request, "ids", limit=5)
            assert result == ["1", "2", "3"]

    def test_process_list_input_missing(self, flask_app):
        with flask_app.test_request_context("/"):
            with pytest.raises(BadRequest) as exc:
                process_list_input(request, "ids", limit=5)
            assert "No ids provided" in str(exc.value)

    def test_process_list_input_missing_post(self, flask_app):
        with flask_app.test_request_context("/", method="POST", json={}):
            with pytest.raises(BadRequest) as exc:
                process_list_input(request, "ids", limit=5)
            assert "No ids provided" in str(exc.value)

    def test_process_list_input_exceeds_limit(self, flask_app):
        with flask_app.test_request_context("/?ids=1,2,3,4,5,6"):
            with pytest.raises(BadRequest) as exc:
                process_list_input(request, "ids", limit=5)
            assert "exceeded limit" in str(exc.value)

    def test_process_list_input_exceeds_limit_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": ["1", "2", "3", "4", "5", "6"]}
        ):
            with pytest.raises(BadRequest) as exc:
                process_list_input(request, "ids", limit=5)
            assert "exceeded limit" in str(exc.value)


class TestProcessIntegerListInput:
    def test_process_integer_list_input_valid(self, flask_app):
        with flask_app.test_request_context("/?ids=1,2,3"):
            result = process_integer_list_input(request, "ids", limit=5)
            assert result == [1, 2, 3]

    def test_process_integer_list_input_valid_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": ["1", "2", "3"]}
        ):
            result = process_integer_list_input(request, "ids", limit=5)
            assert result == [1, 2, 3]

    def test_process_integer_list_input_valid_post_integers(self, flask_app):
        """Test with actual integers in JSON (not strings)"""
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": [1, 2, 3]}
        ):
            result = process_integer_list_input(request, "ids", limit=5)
            assert result == [1, 2, 3]

    def test_process_integer_list_input_non_integer(self, flask_app):
        with flask_app.test_request_context("/?ids=1,two,3"):
            with pytest.raises(BadRequest) as exc:
                process_integer_list_input(request, "ids", limit=5)
            assert "contains non-integer elements" in str(exc.value)

    def test_process_integer_list_input_non_integer_post(self, flask_app):
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": ["1", "two", "3"]}
        ):
            with pytest.raises(BadRequest) as exc:
                process_integer_list_input(request, "ids", limit=5)
            assert "contains non-integer elements" in str(exc.value)

    def test_process_integer_list_input_mixed_types_post(self, flask_app):
        """Test with mixed integer and string types in JSON"""
        with flask_app.test_request_context(
            "/", method="POST", json={"ids": [1, "2", 3]}
        ):
            result = process_integer_list_input(request, "ids", limit=5)
            assert result == [1, 2, 3]
