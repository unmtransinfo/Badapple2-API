"""
@author Jack Ringer
Date: 8/19/2025
Description:
Defines unit tests to ensure scaffolds are generated
as expected by method in hiers.py.
"""

from utils.process_scaffolds import get_scaffolds_single_mol, is_valid_scaf


def test_is_valid_scaf():
    """
    GIVEN a SMILES (or Inchi) string representing a scaffold
    WHEN  CustomHierS network is used to generate scaffolds
    THEN returns False if the SMILES/Inchi string is either empty or represents benzene
    Note: Since is_valid_scaf() is just testing outputs from CustomHierS we are assuming that the SMILES/Inchi strings provided are
    either:
    1) Valid molecules
    OR
    2) Empty (this happens when the input compound has no scaffolds)

    is_valid_scaf() thus does not check if the provided string is actually a valid representation of a molecule - that is taken care of elsewhere.
    """
    # empty check
    assert is_valid_scaf("") == False

    # check benzene
    assert is_valid_scaf("C1=CC=CC=C1") == False
    assert is_valid_scaf("c1ccccc1") == False
    assert is_valid_scaf("InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H") == False

    # check other scafs
    assert is_valid_scaf("O=c1oc2cccc3c(=O)oc4cccc1c4c23")
    assert is_valid_scaf("C1CCCCC1")


def test_get_scaffolds_single_mol():
    """
    GIVEN a (possibly invalid) SMILES string representing a chemical compound
    WHEN Processing scaffolds for user-provided compounds (in compound_search.py)
    THEN check that the correct canonical SMILES of all scaffolds are returned
    """
    NULL_NAME = "null"

    def get_scaffolds_only(mol_smiles: str, max_rings: int = 5):
        return get_scaffolds_single_mol(mol_smiles, NULL_NAME, max_rings)["scaffolds"]

    # check that appropriate scaffold(s) returned for valid SMILES inputs
    assert get_scaffolds_only("O=c1oc2cccc3c(=O)oc4cccc1c4c23") == [
        "O=c1oc2cccc3c(=O)oc4cccc1c4c23"
    ]
    assert get_scaffolds_only("O=c1oc2cccc3c(=O)oc4cccc1c4c23") == [
        "O=c1oc2cccc3c(=O)oc4cccc1c4c23"
    ]
    scaffolds = get_scaffolds_only(
        r"CCN(CC)CCNC(=O)c1c(C)[nH]c(/C=C2\C(=O)Nc3ccc(F)cc32)c1C",
    )
    assert len(scaffolds) == 3
    assert "O=C1Nc2ccccc2C1=Cc1ccc[nH]1" in scaffolds
    assert "C=C1C(=O)Nc2ccccc21" in scaffolds
    assert "c1cc[nH]c1" in scaffolds

    # check that max_rings works as expected
    large_mol_smi = "Cn1cc(C2=C(c3cn(C4CCN(Cc5ccccn5)CC4)c4ccccc34)C(=O)NC2=O)c2ccccc21"
    scaffolds = get_scaffolds_only(
        large_mol_smi,
        max_rings=5,
    )  # input mol here has 5 ring systems, is <= max_rings, expected to return 13 scaffolds
    assert len(scaffolds) == 13
    scaffolds = get_scaffolds_only(
        large_mol_smi, max_rings=4
    )  # mol now too big, shouldn't process
    assert scaffolds == []

    # check that compounds with no scaffolds give correct result
    assert (
        get_scaffolds_only("NC(C)Cc1ccccc1", max_rings=5) == []
    )  # benzene is only scaffold of this compound (adderall)
    assert get_scaffolds_only("CCC") == []

    # check handling of invalid SMILES, but should still not return any scaffolds
    assert get_scaffolds_single_mol("", NULL_NAME, max_rings=5) == {}
    assert get_scaffolds_single_mol(" ", NULL_NAME, max_rings=5) == {}
    assert get_scaffolds_single_mol("asdnasjd", NULL_NAME, max_rings=5) == {}
    assert get_scaffolds_single_mol("NC(C)Cc1cdcccc1", NULL_NAME, max_rings=5) == {}
