"""
@author Jack Ringer
Date: 8/29/2024
Description:
Functions related to getting scaffolds from input molecule(s).
"""

import pandas as pd
from utils.scaffolds.hiers import CustomHierS


# NOTE: the functions/lines in scaffolds.hiers and below should match exactly what was used in generate_scaffolds.py
# https://github.com/unmtransinfo/Badapple2/blob/main/src/generate_scaffolds.py
# git submodules could be a cleaner solution, but not worth it for 1 file...
# START OF EXACT MATCH
def is_valid_scaf(scaf_rep: str):
    if len(scaf_rep) == 0:
        # empty string given
        return False
    elif (
        scaf_rep == "c1ccccc1"
        or scaf_rep == "C1=CC=CC=C1"
        or scaf_rep == "InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H"
    ):
        # benzene excluded from scaffolds
        return False
    return True


# END OF EXACT MATCH


def get_mol2scaf_dict(network: CustomHierS) -> dict[str, list[str]]:
    mol_to_scafs = {}
    for mol_node in network.get_molecule_nodes(data=True):
        mol_name = mol_node[0]
        mol_smiles = mol_node[1]["smiles"]
        mol_to_scafs[mol_smiles] = []
        mol_scaffolds = network.get_scaffolds_for_molecule(mol_name, data=True)
        for scaf_node in mol_scaffolds:
            scaf_rep = scaf_node[0]
            if is_valid_scaf(scaf_rep):
                mol_to_scafs[mol_smiles].append(scaf_rep)
    return mol_to_scafs


def get_scaffolds_single_mol(mol_smiles: str, name: str, max_rings: int):
    # setup network
    smiles_dict = {"Smiles": [mol_smiles], "Name": [name]}
    smiles_df = pd.DataFrame.from_dict(smiles_dict)
    network = CustomHierS.from_dataframe(smiles_df, ring_cutoff=max_rings)
    # get scaffolds, convert to json for use with API / UI
    mol2scafs = get_mol2scaf_dict(network)
    if len(mol2scafs.keys()) < 1:
        return {}  # likely invalid Smiles
    # indexing [0] bc we only have 1 input molecule
    result = {
        "molecule_cansmi": list(mol2scafs.keys())[0],
        "scaffolds": list(mol2scafs.values())[0],
    }
    return result
