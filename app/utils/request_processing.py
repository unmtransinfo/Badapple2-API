"""
@author Jack Ringer
Date: 8/3/2024
Description:
Functions related to parsing requests.
"""

from typing import Union

from config import MAX_RING_LOWER_BOUND, MAX_RING_UPPER_BOUND
from flask import abort


def int_check(
    n,
    var_name: str,
    lower_limit: Union[None, int] = None,
    upper_limit: Union[None, int] = None,
):
    try:
        n = int(n)
    except:
        return abort(400, f"Invalid {var_name} provided. Expected int but got: {n}")
    if lower_limit is not None and n < lower_limit:
        return abort(400, f"Error: {var_name} must be greater than {lower_limit}")
    if upper_limit is not None and n > upper_limit:
        return abort(400, f"Error: {var_name} must be less than {upper_limit}")
    return n


def get_max_rings(request, default_val: int = 10):
    max_rings = request.args.get("max_rings", type=int) or default_val
    max_rings = int_check(
        max_rings,
        "max_rings",
        MAX_RING_LOWER_BOUND,
        MAX_RING_UPPER_BOUND,
    )
    return max_rings


def process_list_input(request, param_name: str, limit: int):
    value_list = request.args.get(param_name, type=str)
    if not value_list:
        return abort(400, f"No {param_name} provided")
    value_list = value_list.split(",")
    if len(value_list) > limit:
        return abort(
            400,
            f"Provided list of {param_name} exceeded limit of {limit}. Please provide <= {limit} {param_name} at a time.",
        )
    return value_list


def process_integer_list_input(request, param_name: str, limit):
    int_list = process_list_input(request, param_name, limit)
    try:
        int_list = [int(cid) for cid in int_list]
    except ValueError:
        return abort(
            400,
            f"Provided list of {param_name} contains non-integer elements. Please check input.",
        )
    return int_list
