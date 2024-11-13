"""
@author Jack Ringer
Date: 7/10/2024
Description:
API call for getting scaffolds using HierS algo.
"""

from config import MAX_RING_LOWER_BOUND, MAX_RING_UPPER_BOUND
from flasgger import swag_from
from flask import Blueprint, abort, jsonify, request
from utils.process_scaffolds import get_scaffolds_single_mol
from utils.request_processing import get_max_rings

hiers_api = Blueprint("hiers", __name__, url_prefix="/hiers")


@hiers_api.route("/get_scaffolds", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "SMILES",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "Input molecule SMILES",
            },
            {
                "name": "name",
                "in": "query",
                "type": "string",
                "default": "",
                "required": False,
                "description": "Input molecule name",
            },
            {
                "name": "max_rings",
                "in": "query",
                "type": "integer",
                "default": 10,
                "required": False,
                "description": "Ignore molecules with more than the specified number of ring systems to avoid extended processing times",
                "minimum": MAX_RING_LOWER_BOUND,
                "maximum": MAX_RING_UPPER_BOUND,
            },
        ],
        "responses": {
            200: {
                "description": "A json object with the list of scaffolds (as SMILES)"
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_scaffolds():
    """
    Return scaffolds for a single input molecule.
    Scaffolds are derived using the HierS algorithm:
    https://pubs.acs.org/doi/10.1021/jm049032d.
    """
    mol_smiles = request.args.get("SMILES", type=str)
    name = request.args.get("name", type=str) or ""
    max_rings = get_max_rings(request)
    result = get_scaffolds_single_mol(mol_smiles, name, max_rings)
    if result == {}:
        return abort(400, "Invalid SMILES provided")
    return jsonify(result)
