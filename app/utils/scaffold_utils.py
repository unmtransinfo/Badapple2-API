"""
@author Jack Ringer
Date: 8/29/2024
Description:
Functions related to getting scaffolds from input molecule(s).
"""

import pandas as pd
import scaffoldgraph as sg
from loguru import logger
from rdkit import Chem
from scaffoldgraph.core.fragment import (
    get_annotated_murcko_scaffold,
    get_murcko_scaffold,
)
from scaffoldgraph.core.scaffold import Scaffold


# NOTE: the functions/lines below should match exactly what was used in generate_scaffolds.py
# https://github.com/unmtransinfo/Badapple2/blob/main/src/generate_scaffolds.py
# git submodules could be a cleaner solution, but not worth it for 1 file...
# START OF EXACT MATCH
def canon_smiles(mol: Chem.Mol, kekule=False):
    try:
        # need to convert twice to cover edge cases
        canon_smiles = Chem.MolToSmiles(mol, canonical=True, kekuleSmiles=kekule)
        canon_smiles = Chem.MolToSmiles(
            Chem.MolFromSmiles(canon_smiles), canonical=True, kekuleSmiles=kekule
        )
        return canon_smiles
    except:
        original_smiles = Chem.MolToSmiles(mol)
        return original_smiles


class CustomHierS(sg.HierS):
    """
    This is a slightly modified version of the original HierS algorithm from ScaffoldGraph. it uses the following changes:
    1) Includes molecules with no top-level scaffold in the graph.
    2) Supports multiple identifier types, rather than only canonical aromatic SMILES
    """

    def __init__(self, *args, identifier_type="canon_smiles", **kwargs):
        super().__init__(*args, **kwargs)
        # Track scaffolds that couldn't be Kekulized
        # (these structures are invalid for RDKit PostgreSQL cartridge)
        self.non_kekule_scaffolds = set()
        self.identifier_type = identifier_type
        if identifier_type == "canon_smiles":
            self.hash_func = canon_smiles
        elif identifier_type == "kekule_smiles":
            self.hash_func = lambda mol: canon_smiles(mol, kekule=True)
        elif identifier_type == "inchi":
            self.hash_func = Chem.MolToInchi
        else:
            raise ValueError(f"Unrecognized identifier_type: {identifier_type}")

    def _process_no_top_level(self, molecule):
        """Private: Process molecules with no top-level scaffold.
        Modified from original code so that molecules with no top-level
        scaffold are still included in the graph.
        Parameters
        ----------
        molecule : rdkit.Chem.rdchem.Mol
            An rdkit molecule determined to have no top-level scaffold.
        """
        name = molecule.GetProp("_Name")
        logger.info(f"No top level scaffold for molecule: {name}")
        self.graph["num_linear"] = self.graph.get("num_linear", 0) + 1
        self.add_molecule_node(
            molecule,
        )
        return None

    def _initialize_scaffold(self, molecule, init_args):
        """Initialize the top-level scaffold for a molecule.
        Modified from the original code to Kekulize the scaffold.

        Initialization generates a murcko scaffold, performs
        any preprocessing required and then adds the scaffold
        node to the graph connecting it to its child molecule.
        This process can be customised in subclasses to modify
        how a scaffold is initialized.

        Parameters
        ----------
        molecule : rdkit.Chem.rdchem.Mol
            A molecule from whicg to initialize a scaffold.
        init_args : dict
            A dictionary containing arguments for scaffold
            initialization and preprocessing.

        Returns
        -------
        scaffold : Scaffold
            A Scaffold object containing the initialized
            scaffold to be processed further (hierarchy
            generation).

        """
        scaffold_rdmol = get_murcko_scaffold(molecule)
        if scaffold_rdmol.GetNumAtoms() <= 0:
            return self._process_no_top_level(molecule)
        scaffold_rdmol = self._preprocess_scaffold(scaffold_rdmol, init_args)
        scaffold = Scaffold(scaffold_rdmol)
        # CHANGE: override default hash_func
        scaffold.hash_func = self.hash_func
        # END CHANGE
        annotation = None
        if init_args.get("annotate") is True:
            annotation = get_annotated_murcko_scaffold(molecule, scaffold_rdmol, False)
        self.add_scaffold_node(scaffold)
        self.add_molecule_node(molecule)
        self.add_molecule_edge(molecule, scaffold, annotation=annotation)
        return scaffold

    def _hierarchy_constructor(self, child):
        parents = (p for p in self.fragmenter.fragment(child) if p)
        for parent in parents:
            # CHANGE: use consistent hash_func as in _initialize_scaffold
            parent.hash_func = self.hash_func
            # END CHANGE
            if parent in self.nodes:
                self.add_scaffold_edge(parent, child)
            else:
                self.add_scaffold_node(parent)
                self.add_scaffold_edge(parent, child)
                if parent.ring_systems.count > 1:
                    self._hierarchy_constructor(parent)


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


def get_scaffolds_single_mol(mol_smiles: str, name: str, ring_cutoff: int):
    # setup network
    smiles_dict = {"Smiles": [mol_smiles], "Name": [name]}
    smiles_df = pd.DataFrame.from_dict(smiles_dict)
    network = CustomHierS.from_dataframe(smiles_df, ring_cutoff=ring_cutoff)
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
