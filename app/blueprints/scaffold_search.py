"""
@author Jack Ringer
Date: 8/29/2024
Description:
Blueprint for searching Badapple DB for data from scaffold inputs.
For information on what each of the API calls do see api_spec.yml.
"""

from config import ALLOWED_DB_NAMES
from database.badapple import BadAppleSession
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database, get_required_param, int_check
from utils.result_processing import process_singleton_list

scaffold_search = Blueprint("scaffold_search", __name__, url_prefix="/scaffold_search")
TAGS = ["Scaffold Search"]


@scaffold_search.route("/get_scaffold_id", methods=["GET"])
def get_scaffold_id():
    scaf_smiles = get_required_param(request, "SMILES", type=str)
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_scaffold_id(scaf_smiles)
    result = process_singleton_list(result)["id"]
    return jsonify(result)


@scaffold_search.route("/get_scaffold_info", methods=["GET"])
def get_scaffold_info():
    scafid = int_check(request, "scafid")
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.search_scaffold_by_id(scafid)
    result = process_singleton_list(result)
    return jsonify(result)


@scaffold_search.route("/get_associated_compounds", methods=["GET"])
def get_associated_compounds():
    scafid = int_check(request, "scafid")
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_associated_compounds(scafid)
    return jsonify(result)


# these routes are conditional on IN_PROD flag
# (see version.py)
def include_dev_only_routes():
    @scaffold_search.route("/get_associated_assay_ids", methods=["GET"])
    def get_associated_assay_ids():
        scafid = int_check(request, "scafid")
        db_name = get_database(request)
        with BadAppleSession(db_name) as db_session:
            result = db_session.get_associated_assay_ids(scafid)
        result = [d["aid"] for d in result]
        return jsonify(result)


# badapple2+ only
def _get_processed_result(result: list[dict]) -> list[dict]:
    # remove null data
    processed_result = []
    for d in result:
        d_processed = {}
        for key in d:
            if d[key] is not None:
                d_processed[key] = d[key]
        processed_result.append(d_processed)
    return processed_result


@scaffold_search.route("/get_active_targets", methods=["GET"])
def get_active_targets():
    scafid = int_check(request, "scafid")
    db_name = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_active_targets(scafid)
    processed_result = _get_processed_result(result)
    return jsonify(processed_result)


@scaffold_search.route("/get_active_assay_details", methods=["GET"])
def get_active_assay_details():
    # gets same info as get_active_targets, but also includes BARD annotations
    # slightly slower than get_active_targets so creating separate route
    scafid = int_check(request, "scafid")
    db_name = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_active_assay_details(scafid)
    processed_result = _get_processed_result(result)
    return jsonify(processed_result)


@scaffold_search.route("/get_associated_drugs", methods=["GET"])
def get_associated_drugs():
    scafid = int_check(request, "scafid")
    db_name = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_associated_drugs(scafid)
    return jsonify(result)
