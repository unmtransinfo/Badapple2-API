"""
@author Jack Ringer
Date: 8/28/2024
Description:
Blueprint for searching Badapple DB for data from compound inputs.
For information on what each of the API calls do see api_spec.yml.
"""

from collections import defaultdict

import psycopg2
import psycopg2.extras
from database import badapple
from flask import Blueprint, abort, jsonify, request
from utils.process_scaffolds import get_scaffolds_single_mol
from utils.request_processing import (
    get_database,
    get_max_rings,
    process_integer_list_input,
    process_list_input,
)

compound_search = Blueprint("compound_search", __name__, url_prefix="/compound_search")


def _get_associated_scaffolds_from_list(
    smiles_list: list[str], max_rings: int, db_name: str
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
        db_connection = badapple.connect(db_name)
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        for scafsmi in scaffolds:
            scaf_info = badapple.search_scaffold_by_smiles(
                scafsmi, db_name, db_connection, db_cursor
            )
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
    db_cursor.close()
    db_connection.close()
    return result


@compound_search.route("/get_associated_scaffolds", methods=["GET"])
def get_associated_scaffolds():
    smiles_list = process_list_input(request, "SMILES", 1000)
    max_rings = get_max_rings(request)
    database = get_database(request)
    result = _get_associated_scaffolds_from_list(smiles_list, max_rings, database)
    return jsonify(result)


@compound_search.route("/get_associated_scaffolds_ordered", methods=["GET"])
def get_associated_scaffolds_ordered():
    smiles_list = process_list_input(request, "SMILES", 1000)
    max_rings = get_max_rings(request)
    database = get_database(request)
    name_list = smiles_list
    names_given = "Names" in request.args
    if names_given:
        name_list = process_list_input(request, "Names", 1000)
        if len(smiles_list) != len(name_list):
            return abort(
                400,
                f"Length of 'SMILES' and 'Names' list expected to match, but got lengths: {len(smiles_list)} and {len(name_list)}",
            )
    smiles2scaffolds = _get_associated_scaffolds_from_list(
        smiles_list, max_rings, database
    )
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


@compound_search.route("/get_associated_substance_ids", methods=["GET"])
def get_associated_substance_ids():
    cid_list = process_integer_list_input(request, "CIDs", 1000)
    database = get_database(request)
    result = badapple.get_associated_sids(cid_list, database)

    # combine dicts with shared CID
    combined_result = defaultdict(list)
    for item in result:
        combined_result[item["cid"]].append(item["sid"])

    formatted_result = [
        {"CID": cid, "SIDs": sids} for cid, sids in combined_result.items()
    ]
    return jsonify(formatted_result)
