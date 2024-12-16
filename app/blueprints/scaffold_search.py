"""
@author Jack Ringer
Date: 8/29/2024
Description:
Blueprint for searching Badapple DB for data from scaffold inputs.
For information on what each of the API calls do see api_spec.yml.
"""

from config import ALLOWED_DB_NAMES
from database import badapple
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database

scaffold_search = Blueprint("scaffold_search", __name__, url_prefix="/scaffold_search")
TAGS = ["Scaffold Search"]


@scaffold_search.route("/get_scaffold_id", methods=["GET"])
def get_scaffold_id():
    scaf_smiles = request.args.get("SMILES", type=str)
    database = get_database(request)
    result = badapple.get_scaffold_id(scaf_smiles, database)
    if result and len(result) > 0:
        result = result[0]["id"]
    else:
        result = None
    return jsonify(result)


@scaffold_search.route("/get_associated_compounds", methods=["GET"])
def get_associated_compounds():
    scafid = request.args.get("scafid", type=int)
    database = get_database(request)
    result = badapple.get_associated_compounds(scafid, database)
    return jsonify(result)


@scaffold_search.route("/get_associated_assay_ids", methods=["GET"])
def get_associated_assay_ids():
    scafid = request.args.get("scafid", type=int)
    database = get_database(request)
    result = badapple.get_associated_assay_ids(scafid, database)
    result = [d["aid"] for d in result]
    return jsonify(result)


# badapple2+ only
@scaffold_search.route("/get_active_targets", methods=["GET"])
def get_active_targets():
    scafid = request.args.get("scafid", type=int)
    database = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    result = badapple.get_active_targets(scafid, database)
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
    scafid = request.args.get("scafid", type=int)
    database = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    result = badapple.get_associated_drugs(scafid, database)
    return jsonify(result)
