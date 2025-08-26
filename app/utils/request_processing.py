"""
@author Jack Ringer
Date: 8/3/2024
Description:
Functions related to parsing requests.
"""

from typing import Union

from config import (
    ALLOWED_DB_NAMES,
    DEFAULT_DB,
    MAX_LIST_LENGTH,
    MAX_RING_DEFAULT,
    MAX_RING_LOWER_BOUND,
    MAX_RING_UPPER_BOUND,
)
from flask import abort


def _method_not_supported(request):
    return abort(405, f"Method {request.method} not supported")


def param_given(request, param_name: str):
    param_given = False
    if request.method == "GET":
        param_given = param_name in request.args
    elif request.method == "POST":
        param_given = param_name in request.json
    else:
        return _method_not_supported(request)
    return param_given


def get_param(request, param_name: str, type, default_val=None):
    val = None
    if request.method == "GET":
        val = request.args.get(param_name, type=type)
    elif request.method == "POST":
        val = request.json.get(param_name)
    else:
        return _method_not_supported(request)
    if val is None:
        val = default_val
    return val


def get_required_param(request, param_name: str, type):
    val = get_param(request, param_name, type)
    if not val:  # None or empty
        return abort(400, f"No {param_name} provided")
    return val


def int_check(
    request,
    var_name: str,
    lower_limit: Union[None, int] = None,
    upper_limit: Union[None, int] = None,
    default_val: Union[None, int] = None,
):
    n = get_param(request, var_name, type=int, default_val=default_val)
    try:
        n = int(n)
    except:
        return abort(
            400,
            f"Invalid {var_name} provided. Expected int but got: {request.args.get(var_name)}",
        )
    if lower_limit is not None and n < lower_limit:
        return abort(400, f"Error: {var_name} must be greater than {lower_limit}")
    if upper_limit is not None and n > upper_limit:
        return abort(400, f"Error: {var_name} must be less than {upper_limit}")
    return n


def get_max_rings(request):
    max_rings = int_check(
        request,
        "max_rings",
        MAX_RING_LOWER_BOUND,
        MAX_RING_UPPER_BOUND,
        MAX_RING_DEFAULT,
    )
    return max_rings


def get_database(
    request,
    default_val: str = DEFAULT_DB,
    allowed_db_names: list[str] = ALLOWED_DB_NAMES,
):
    database = get_param(request, "database", type=str, default_val=default_val)
    if database not in allowed_db_names:
        db_names = ",".join(allowed_db_names)
        return abort(400, f"Invalid database provided, select from: {db_names}")
    return database


def process_list_input(request, param_name: str, limit: int = MAX_LIST_LENGTH):
    value_list = get_required_param(request, param_name, type=str)
    if request.method == "GET":
        value_list = value_list.split(",")
    if len(value_list) > limit:
        return abort(
            400,
            f"Provided list of {param_name} exceeded limit of {limit}. Please provide <= {limit} {param_name} at a time.",
        )
    return value_list


def process_integer_list_input(request, param_name: str, limit: int = MAX_LIST_LENGTH):
    int_list = process_list_input(request, param_name, limit)
    try:
        int_list = [int(x) for x in int_list]
    except ValueError:
        return abort(
            400,
            f"Provided list of {param_name} contains non-integer elements. Please check input.",
        )
    return int_list
