"""
@author Jack Ringer
Date: 10/3/2024
Description:
API calls with substance (SID) inputs.
"""

from config import ALLOWED_DB_NAMES
from database import badapple
from flasgger import swag_from
from flask import Blueprint, jsonify, request
from utils.request_processing import get_database

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
    database = get_database(request)
    result = badapple.get_assay_outcomes(sid, database)
    return jsonify(result)
