"""
@author Jack Ringer
Date: 8/21/2025
Description:
Helper functions for tests
"""


def validate_keys(d: dict, expected_keys: list):
    assert set(expected_keys).issubset(d.keys())


def validate_scaffold_keys(d: dict):
    """Validate that all rows from scaffold table included in result"""
    expected_keys = [
        "id",
        "in_drug",
        "kekule_scafsmi",
        "nass_active",
        "nass_tested",
        "ncpd_active",
        "ncpd_tested",
        "ncpd_total",
        "nsam_active",
        "nsam_tested",
        "nsub_active",
        "nsub_tested",
        "nsub_total",
        "prank",
        "pscore",
        "scafsmi",
        "scaftree",
    ]
    validate_keys(d, expected_keys)


def validate_compound_keys(d: dict):
    """Validate that all rows from compound table included in result"""
    expected_keys = [
        "cid",
        "cansmi",
        "isosmi",
        "nsub_total",
        "nsub_tested",
        "nsub_active",
        "nass_tested",
        "nass_active",
        "nsam_tested",
        "nsam_active",
    ]
    validate_keys(d, expected_keys)


def validate_target_keys(d: dict):
    expected_keys = [
        "target_id",
        "type",
        "external_id",
        "external_id_type",
        "name",
        "taxonomy",
        "taxonomy_id",
        "protein_family",
    ]
    validate_keys(d, expected_keys)


def validate_drug_keys(d: dict):
    """Validate that all rows from the drug table included in result"""
    expected_keys = ["drug_id", "cansmi", "inn"]
    validate_keys(d, expected_keys)
