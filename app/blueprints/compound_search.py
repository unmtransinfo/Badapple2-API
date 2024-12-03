"""
@author Jack Ringer
Date: 8/28/2024
Description:
Blueprint for searching Badapple DB for data from compound inputs.
"""

from collections import defaultdict

from config import MAX_RING_LOWER_BOUND, MAX_RING_UPPER_BOUND
from database.badapple_classic import BadappleClassicDB
from flasgger import swag_from
from flask import Blueprint, abort, jsonify, request
from utils.process_scaffolds import get_scaffolds_single_mol
from utils.request_processing import (
    get_max_rings,
    process_integer_list_input,
    process_list_input,
)

compound_search = Blueprint("compound_search", __name__, url_prefix="/compound_search")


def _get_associated_scaffolds_from_list(
    smiles_list: list[str], max_rings: int
) -> dict[str, list]:
    """
    Helper function, returns a dictionary mapping SMILES to associated scaffolds + info.
    """
    result = {}

    for smiles in smiles_list:
        scaf_res = get_scaffolds_single_mol(smiles, name="", max_rings=max_rings)
        if scaf_res == {}:
            # ignore invalid SMILES
            continue

        scaffolds = scaf_res["scaffolds"]
        scaffold_info_list = []
        for scafsmi in scaffolds:
            scaf_info = BadappleClassicDB.search_scaffold(scafsmi)
            if len(scaf_info) < 1:
                scaf_info = {
                    "scafsmi": scafsmi,
                    "in_db": False,
                }
            else:
                scaf_info = dict(scaf_info[0])
                scaf_info["in_db"] = True
            scaffold_info_list.append(scaf_info)

        result[smiles] = scaffold_info_list
    return result


@compound_search.route("/get_associated_scaffolds", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "SMILES",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "List of compound SMILES, comma-separated. Invalid SMILES are ignored.",
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
                "description": "A json object with all compounds and their associated scaffolds + their information. Note that if a scaffold is not present in the DB it will have an empty list instead of info."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_associated_scaffolds():
    """
    Return associated scaffolds + info on each, dictionary from input SMILES->scaffolds.
    """
    smiles_list = process_list_input(request, "SMILES", 1000)
    max_rings = get_max_rings(request)
    result = _get_associated_scaffolds_from_list(smiles_list, max_rings)
    return jsonify(result)


@compound_search.route("/get_associated_scaffolds_ordered", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "SMILES",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "List of compound SMILES, comma-separated. ",
            },
            {
                "name": "Names",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "List of compound names, comma-separated.",
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
                "description": "A json object with all compounds and their associated scaffolds. The data will be in the same order as the given list of SMILES/Names."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_associated_scaffolds_ordered():
    """
    Return associated scaffolds + info on each, list in order of input.
    """
    smiles_list = process_list_input(request, "SMILES", 1000)
    max_rings = get_max_rings(request)
    name_list = smiles_list
    names_given = "Names" in request.args
    if names_given:
        name_list = process_list_input(request, "Names", 1000)
        if len(smiles_list) != len(name_list):
            return abort(
                400,
                f"Length of 'SMILES' and 'Names' list expected to match, but got lengths: {len(smiles_list)} and {len(name_list)}",
            )
    smiles2scaffolds = _get_associated_scaffolds_from_list(smiles_list, max_rings)
    # order output
    # one could optimize/re-write _get_associated_scaffolds_from_list for this API call, but not expecting to deal with large inputs
    result = []
    for smiles, name in zip(smiles_list, name_list):
        d = {"molecule_smiles": smiles, "name": name}
        if smiles in smiles2scaffolds:
            d["scaffolds"] = smiles2scaffolds[smiles]
        else:
            d["scaffolds"] = None
            d["error_msg"] = "Invalid SMILES, please check input"
        result.append(d)
    return jsonify(result)


@compound_search.route("/get_high_scores", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "SMILES",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "List of compound SMILES, comma-separated. Invalid SMILES are ignored.",
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
                "description": "A json object with all compounds and their highest-scoring scaffold + its pscore. If the compound has no scaffolds in the DB a score of 'None' is given."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_high_scores():
    """
    Return highest-scoring scaffold for each molecule.
    """
    smiles_list = process_list_input(request, "SMILES", 1000)
    max_rings = get_max_rings(request)
    associated_scaffolds = _get_associated_scaffolds_from_list(smiles_list, max_rings)
    result = []
    for smiles in associated_scaffolds.keys():
        scaffolds = associated_scaffolds[smiles]
        max_scaf_score = -1
        max_scaf_info = {}
        for scaf_info in scaffolds:
            if scaf_info["in_db"]:
                scaf_pscore = scaf_info["pscore"]
                if scaf_pscore is not None and scaf_pscore > max_scaf_score:
                    max_scaf_score = scaf_pscore
                    max_scaf_info = scaf_info
        if max_scaf_score == -1:
            max_scaf_score = None
        result.append(
            {
                "molecule_smiles": smiles,
                "highest_scoring_scaf": max_scaf_info,
            }
        )

    return jsonify(result)


@compound_search.route("/get_associated_substance_ids", methods=["GET"])
@swag_from(
    {
        "parameters": [
            {
                "name": "CIDs",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "List of compound PubChem CIDs, comma-separated.",
            },
        ],
        "responses": {
            200: {
                "description": "A json object containing each CID mapped to 1 or more SIDs associated with it in the DB. CIDs not in the DB will have 0 associated SIDs."
            },
            400: {"description": "Malformed request error"},
        },
    }
)
def get_associated_substance_ids():
    """
    Get SubstanceIDs (SIDs) associated with the input CompoundIDs (CIDs) in the DB.
    """
    cid_list = process_integer_list_input(request, "CIDs", 1000)
    result = BadappleClassicDB.get_associated_sids(cid_list)

    # combine dicts with shared CID
    combined_result = defaultdict(list)
    for item in result:
        combined_result[item["cid"]].append(item["sid"])

    formatted_result = [
        {"CID": cid, "SIDs": sids} for cid, sids in combined_result.items()
    ]
    return jsonify(formatted_result)
