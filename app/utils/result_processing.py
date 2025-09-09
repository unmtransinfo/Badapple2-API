"""
@author Jack Ringer
Date: 9/9/2025
Description:
Utils to help process results from SQL queries before jsonify.
"""


def process_singleton_list(result: list) -> dict:
    # for endpoints where we know the result is a list of length 1
    if result and len(result) > 0:
        result = result[0]
    else:
        result = None
    return result
