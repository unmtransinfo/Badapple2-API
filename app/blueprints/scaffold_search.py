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

scaffold_search = Blueprint("scaffold_search", __name__, url_prefix="/scaffold_search")
TAGS = ["Scaffold Search"]


@scaffold_search.route("/get_scaffold_id", methods=["GET"])
def get_scaffold_id():
    scaf_smiles = get_required_param(request, "SMILES", type=str)
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_scaffold_id(scaf_smiles)
    if result and len(result) > 0:
        result = result[0]["id"]
    else:
        result = None
    return jsonify(result)


@scaffold_search.route("/get_scaffold_info", methods=["GET"])
def get_scaffold_info():
    scafid = int_check(request, "scafid")
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.search_scaffold_by_id(scafid)
    if result and len(result) > 0:
        result = result[0]
    else:
        result = None
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
@scaffold_search.route("/get_active_targets", methods=["GET"])
def get_active_targets():
    scafid = int_check(request, "scafid")
    db_name = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_active_targets(scafid)
    processed_result = []
    for d in result:
        if d["external_id"] is None:
            # assay had no target
            processed_result.append({"aid": d["aid"]})
        else:
            processed_result.append(d)
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
