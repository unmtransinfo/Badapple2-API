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
