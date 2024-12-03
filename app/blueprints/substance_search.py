"""
@author Jack Ringer
Date: 10/3/2024
Description:
API calls with substance (SID) inputs.
"""

from database.badapple_classic import BadappleClassicDB
from flasgger import swag_from
from flask import Blueprint, jsonify, request

substance_search = Blueprint(
    "substance_search", __name__, url_prefix="/substance_search"
)


@substance_search.route("/get_assay_outcomes", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "SID",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "PubChem SubstanceID (SID).",
            },
        ],
        "responses": {
            200: {
                "description": "A json object containing a list of AIDs associated with the SID in the DB, with outcomes."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_assay_outcomes():
    """
    Get a list of all PubChem assays (AIDs) associated with the SID in the DB, with outcomes.
    """
    sid = request.args.get("SID", type=int)
    result = BadappleClassicDB.get_assay_outcomes(sid)
    return jsonify(result)
