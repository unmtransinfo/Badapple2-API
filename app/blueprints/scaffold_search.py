"""
@author Jack Ringer
Date: 8/29/2024
Description:
Blueprint for searching Badapple DB for data from scaffold inputs.
"""

from config import ALLOWED_DB_NAMES
from database import badapple
from flasgger import swag_from
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database

scaffold_search = Blueprint("scaffold_search", __name__, url_prefix="/scaffold_search")
TAGS = ["Scaffold Search"]


@scaffold_search.route("/get_scaffold_id", methods=["GET"])
@swag_from(
    {
        "tags": TAGS,
        "parameters": [
            {
                "name": "SMILES",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "SMILES string representing scaffold",
            },
            {
                "name": "database",
                "in": "query",
                "type": "str",
                "default": ALLOWED_DB_NAMES[0],
                "required": False,
                "description": f"Database to fetch information from",
                "enum": ALLOWED_DB_NAMES,
            },
        ],
        "responses": {
            200: {
                "description": "Fetch the scaffoldID (scafid) of the given scaffold using structural search. Note that the scafid for the same scaffold can differ between databases."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_scaffold_id():
    """
    Return the scafid of the given scaffold, null if scaffold not found in DB.
    """
    scaf_smiles = request.args.get("SMILES", type=str)
    database = get_database(request)
    result = badapple.get_scaffold_id(scaf_smiles, database)
    if result and len(result) > 0:
        result = result[0]["id"]
    else:
        result = None
    return jsonify(result)


@scaffold_search.route("/get_associated_compounds", methods=["GET"])
@swag_from(
    {
        "tags": TAGS,
        "parameters": [
            {
                "name": "scafid",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of scaffold.",
            },
            {
                "name": "database",
                "in": "query",
                "type": "str",
                "default": ALLOWED_DB_NAMES[0],
                "required": False,
                "description": f"Database to fetch information from",
                "enum": ALLOWED_DB_NAMES,
            },
        ],
        "responses": {
            200: {
                "description": "List of PubChem compounds associated with the scaffold, including statistics."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_associated_compounds():
    """
    Return all PubChem compounds in the DB known to be associated with the given scaffold ID.
    """
    scafid = request.args.get("scafid", type=int)
    database = get_database(request)
    result = badapple.get_associated_compounds(scafid, database)
    return jsonify(result)


@scaffold_search.route("/get_associated_assay_ids", methods=["GET"])
@swag_from(
    {
        "tags": TAGS,
        "parameters": [
            {
                "name": "scafid",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of scaffold.",
            },
            {
                "name": "database",
                "in": "query",
                "type": "str",
                "default": ALLOWED_DB_NAMES[0],
                "required": False,
                "description": f"Database to fetch information from",
                "enum": ALLOWED_DB_NAMES,
            },
        ],
        "responses": {
            200: {
                "description": "List of PubChem assay IDs associated with the scaffold. Does not include outcomes."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_associated_assay_ids():
    """
    Return all PubChem assay IDs in the DB known to be associated with the given scaffold ID.
    """
    scafid = request.args.get("scafid", type=int)
    database = get_database(request)
    result = badapple.get_associated_assay_ids(scafid, database)
    result = [d["aid"] for d in result]
    return jsonify(result)


# badapple2+ only
@scaffold_search.route("/get_active_targets", methods=["GET"])
@swag_from(
    {
        "tags": TAGS,
        "parameters": [
            {
                "name": "scafid",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of scaffold.",
            },
            {
                "name": "database",
                "in": "query",
                "type": "str",
                "default": ALLOWED_DB_NAMES[1],
                "required": False,
                "description": f"Database to fetch information from",
                "enum": [ALLOWED_DB_NAMES[1]],  # badapple2+ only
            },
        ],
        "responses": {
            200: {
                "description": "List of biological targets where the scaffold was present in a substance 'active' against said target. The corresponding PubChem AssayIDs are also provided."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_active_targets():
    """
    Return the biological targets where the given scafid was present in an 'active' substance, along with corresponding PubChem AssayIDs.
    """
    scafid = request.args.get("scafid", type=int)
    database = get_database(
        request, default_val=ALLOWED_DB_NAMES[1], allowed_db_names=[ALLOWED_DB_NAMES[1]]
    )
    result = badapple.get_active_targets(scafid, database)
    return jsonify(result)
