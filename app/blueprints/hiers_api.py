"""
@author Jack Ringer
Date: 7/10/2024
Description:
API call for getting scaffolds using HierS algo.
"""

from flasgger import swag_from
from flask import Blueprint, abort, jsonify, request

from app.utils.process_scaffolds import get_scaffolds_single_mol

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
                "description": "input molecule SMILES",
            },
            {
                "name": "name",
                "in": "query",
                "type": "string",
                "default": "",
                "required": False,
                "description": "input molecule name",
            },
            {
                "name": "ring_cutoff",
                "in": "query",
                "type": "integer",
                "default": 10,
                "required": False,
                "description": "ignore molecules with more than the specified number of rings to avoid extended processing times",
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
    ring_cutoff = request.args.get("ring_cutoff", type=int) or 10
    result = get_scaffolds_single_mol(mol_smiles, name, ring_cutoff)
    if result == {}:
        return abort(400, "Invalid SMILES provided")
    return jsonify(result)
