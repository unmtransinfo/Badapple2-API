"""
@author Jack Ringer
Date: 8/28/2024
Description:
Blueprint for searching Badapple DB for data from compound inputs.
For information on what each of the API calls do see api_spec.yml.
"""

from collections import defaultdict

from database.badapple import BadAppleSession
from flask import Blueprint, abort, jsonify, request
from utils.process_scaffolds import get_scaffolds_single_mol
from utils.request_processing import (
    get_database,
    get_max_rings,
    param_given,
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
    with BadAppleSession(db_name) as db_session:
        for smiles in smiles_list:
            scaf_res = get_scaffolds_single_mol(smiles, name="", max_rings=max_rings)
            if scaf_res == {}:
                # ignore invalid SMILES
                continue

            scaffolds = scaf_res["scaffolds"]
            scaffold_info_list = []
            for scafsmi in scaffolds:
                scaf_info = db_session.search_scaffold_by_smiles(scafsmi)
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


# process request params for get_associated_scaffolds and get_associated_scaffolds_ordered
def _get_request_params(request):
    smiles_list = process_list_input(request, "SMILES")
    max_rings = get_max_rings(request)
    database = get_database(request)
    name_list = smiles_list
    if param_given(request, "Names"):
        name_list = process_list_input(request, "Names")
    return smiles_list, max_rings, database, name_list


# NOTE: "POST" is allowed here because we want to allow users to submit more than a handful of compounds at a time
# "GET" prevents large requests (max 8190 bytes, as set by gunicorn)
# in an ideal world these methods would use QUERY (https://httpwg.org/http-extensions/draft-ietf-httpbis-safe-method-w-body.html)
# but until QUERY becomes standard we'll have to do with this
# see also: https://medium.com/swlh/why-would-you-use-post-instead-of-get-for-a-read-operation-381e4bdf3b9a
@compound_search.route("/get_associated_scaffolds", methods=["GET", "POST"])
def get_associated_scaffolds():
    smiles_list, max_rings, database, _ = _get_request_params(request)
    result = _get_associated_scaffolds_from_list(smiles_list, max_rings, database)
    return jsonify(result)


@compound_search.route("/get_associated_scaffolds_ordered", methods=["GET", "POST"])
def get_associated_scaffolds_ordered():
    smiles_list, max_rings, database, name_list = _get_request_params(request)
    # sanity check: SMILES/Names lists must match in length
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
    cid_list = process_integer_list_input(request, "CIDs")
    db_name = get_database(request)
    with BadAppleSession(db_name) as db_session:
        result = db_session.get_associated_sids(cid_list)

    # combine dicts with shared CID
    combined_result = defaultdict(list)
    for item in result:
        combined_result[item["cid"]].append(item["sid"])

    formatted_result = [
        {"CID": cid, "SIDs": sids} for cid, sids in combined_result.items()
    ]
    return jsonify(formatted_result)
