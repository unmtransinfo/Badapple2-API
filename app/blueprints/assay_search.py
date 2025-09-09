"""
@author Jack Ringer
Date: 9/9/2025
Description:
API calls with AssayID (AID) inputs.
"""

from config import ALLOWED_DB_NAMES
from database.badapple import BadAppleSession
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database, int_check
from utils.result_processing import process_singleton_list

assay_search = Blueprint("assay_search", __name__, url_prefix="/assay_search")


# badapple2+ only
@assay_search.route("/get_BARD_annotations", methods=["GET"])
def get_BARD_annotations():
    aid = int_check(request, "AID")
    db_name = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_BARD_annotations(aid)
    result = process_singleton_list(result)
    return jsonify(result)
