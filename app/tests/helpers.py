"""
@author Jack Ringer
Date: 8/21/2025
Description:
Helper functions for tests
"""


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
    for ek in expected_keys:
        assert ek in d.keys()
