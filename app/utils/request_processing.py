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
    MAX_RING_LOWER_BOUND,
    MAX_RING_UPPER_BOUND,
)
from flask import abort


def int_check(
    request,
    var_name: str,
    lower_limit: Union[None, int] = None,
    upper_limit: Union[None, int] = None,
    default_val: Union[None, int] = None,
):
    n = request.args.get(var_name, type=int)
    if n is None:
        n = default_val
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


def get_max_rings(request, default_val: int = 10):
    max_rings = int_check(
        request, "max_rings", MAX_RING_LOWER_BOUND, MAX_RING_UPPER_BOUND, default_val
    )
    return max_rings


def get_database(
    request,
    default_val: str = DEFAULT_DB,
    allowed_db_names: list[str] = ALLOWED_DB_NAMES,
):
    database = request.args.get("database", type=str) or default_val
    if database not in allowed_db_names:
        db_names = ",".join(allowed_db_names)
        return abort(400, f"Invalid database provided, select from: {db_names}")
    return database


def get_required_param(request, param_name: str, type):
    val = request.args.get(param_name, type=type)
    if not val:  # None or empty
        return abort(400, f"No {param_name} provided")
    return val


def process_list_input(request, param_name: str, limit: int = MAX_LIST_LENGTH):
    value_list = get_required_param(request, param_name, type=str)
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
        int_list = [int(cid) for cid in int_list]
    except ValueError:
        return abort(
            400,
            f"Provided list of {param_name} contains non-integer elements. Please check input.",
        )
    return int_list
