"""
@author Jack Ringer
Date: 10/3/2024
Description:
API calls with substance (SID) inputs.
"""

from database import badapple
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database, int_check

substance_search = Blueprint(
    "substance_search", __name__, url_prefix="/substance_search"
)


@substance_search.route("/get_assay_outcomes", methods=["GET"])
def get_assay_outcomes():
    sid = int_check(request, "SID")
    database = get_database(request)
    result = badapple.get_assay_outcomes(sid, database)
    return jsonify(result)
