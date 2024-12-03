"""
@author Jack Ringer
Date: 8/29/2024
Description:
Blueprint for searching Badapple DB for data from scaffold inputs.
"""

from database.badapple_classic import BadappleClassicDB
from flasgger import swag_from
from flask import Blueprint, jsonify, request

scaffold_search = Blueprint("scaffold_search", __name__, url_prefix="/scaffold_search")


@scaffold_search.route("/get_associated_compounds", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "scafid",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of scaffold.",
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
    result = BadappleClassicDB.get_associated_compounds(scafid)
    return jsonify(result)


@scaffold_search.route("/get_associated_assay_ids", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "scafid",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of scaffold.",
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
    result = BadappleClassicDB.get_associated_assay_ids(scafid)
    result = [d["aid"] for d in result]
    return jsonify(result)
