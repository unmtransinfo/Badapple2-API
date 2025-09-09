"""
@author Jack Ringer
Date: 9/9/2025
Description:
Functional tests for assay_search blueprint endpoints.
Note here that I'm just checking that the structure of results fetched by the API is correct.
Verifying that the DBs themselves are "accurate" is part of the DB construction.
"""

from tests.helpers import validate_BARD_keys


class TestGetBARDAnnotations:
    """Functional tests for get_BARD_annotations endpoint."""

    def run_test(
        self, test_client, url_prefix, AID=None, database=None, status_code=200
    ):
        """Test runner for get_BARD_annotations endpoint."""
        url = f"{url_prefix}/assay_search/get_BARD_annotations"
        params = []
        if AID is not None:
            params.append(f"AID={AID}")
        if database is not None:
            params.append(f"database={database}")
        if params:
            url += "?" + "&".join(params)

        response = test_client.get(url)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            if data:
                assert isinstance(data, dict)
                validate_BARD_keys(data)

    def test_get_BARD_annotations_valid_aid(self, test_client, url_prefix):
        AID = 360
        self.run_test(test_client, url_prefix, AID)

    def test_get_BARD_annotations_invalid_aid(self, test_client, url_prefix):
        AID = "asm"
        self.run_test(test_client, url_prefix, AID, status_code=400)

    def test_get_BARD_annotations_missing_aid(self, test_client, url_prefix):
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_BARD_annotations_database_parameter(self, test_client, url_prefix):
        AID = 360
        self.run_test(test_client, url_prefix, AID, database="badapple2")

    def test_get_BARD_annotations_bad_database_parameter(self, test_client, url_prefix):
        AID = 360
        self.run_test(
            test_client, url_prefix, AID, database="badapple_classic", status_code=400
        )
