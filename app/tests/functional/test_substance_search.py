"""
@author Jack Ringer
Date: 8/21/2025
Description:
Functional tests for substance_search blueprint endpoints.
Note here that I'm just checking that the structure of results fetched by the API is correct.
Verifying that the DBs themselves are "accurate" is part of the DB construction.
"""

import pytest


@pytest.mark.requires_activity
class TestGetAssayOutcomes:
    """Functional tests for get_assay_outcomes endpoint."""

    def run_test(
        self, test_client, url_prefix, SID=None, database=None, status_code=200
    ):
        """Test runner for get_assay_outcomes endpoint."""
        url = f"{url_prefix}/substance_search/get_assay_outcomes"
        params = []
        if SID is not None:
            params.append(f"SID={SID}")
        if database is not None:
            params.append(f"database={database}")
        if params:
            url += "?" + "&".join(params)

        response = test_client.get(url)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
            for entry in data:
                assert isinstance(entry, dict)
                assert "aid" in entry
                assert "outcome" in entry

    def test_get_assay_outcomes_valid_sid(self, test_client, url_prefix):
        SID = 842121
        self.run_test(test_client, url_prefix, SID)

    def test_get_assay_outcomes_invalid_sid(self, test_client, url_prefix):
        SID = "asm"
        self.run_test(test_client, url_prefix, SID, status_code=400)

    def test_get_assay_outcomes_missing_sid(self, test_client, url_prefix):
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_assay_outcomes_database_parameter(self, test_client, url_prefix):
        SID = 842121
        self.run_test(test_client, url_prefix, SID, database="badapple_classic")
