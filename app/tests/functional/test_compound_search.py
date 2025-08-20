"""
@author Jack Ringer
Date: 8/20/2025
Description:
Functional tests for compound_search blueprint endpoints.
Note here that I'm just checking that the structure of results fetched by the API is correct.
Verifying that the DBs themselves are "accurate" is part of the DB construction.
"""


#
class TestGetAssociatedSubstanceIds:
    """Functional tests for get_associated_substance_ids endpoint."""

    def test_get_associated_substance_ids_multiple_cids(self, test_client, url_prefix):
        """Test with multiple CIDs in the request."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=6,7,8"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert isinstance(data, list)

    def test_get_associated_substance_ids_nonexistent_cid(
        self, test_client, url_prefix
    ):
        """Test with CID that doesn't exist in database."""
        # PubChem does not use negative CIDs
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=-1"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should return empty list for non-existent CIDs
        assert isinstance(data, list)
        # If no associations exist, the API returns an empty list
        assert len(data) == 0

    def test_get_associated_substance_ids_mixed_cids(self, test_client, url_prefix):
        """Test with mix of existing and non-existing CIDs."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=6,-1"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should only return results for CIDs that have associations
        assert isinstance(data, list)

        if len(data) > 0:
            # CID 6 should be in results
            cids_in_response = [item["CID"] for item in data]
            assert 6 in cids_in_response

            # Find result for CID 6
            cid_6_result = next(item for item in data if item["CID"] == 6)
            assert len(cid_6_result["SIDs"]) > 0

    def test_get_associated_substance_ids_missing_parameter(
        self, test_client, url_prefix
    ):
        """Test error handling when CIDs parameter is missing."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids"
        )

        # Should return 400 error for missing required parameter
        assert response.status_code == 400

    def test_get_associated_substance_ids_invalid_cid_format(
        self, test_client, url_prefix
    ):
        """Test error handling with invalid CID format."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=abc,def"
        )

        # Should return 400 error for invalid integer format
        assert response.status_code == 400

    def test_get_associated_substance_ids_empty_cids(self, test_client, url_prefix):
        """Test with empty CIDs parameter."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs="
        )

        # Should handle empty parameter gracefully
        assert response.status_code == 400

    def test_get_associated_substance_ids_large_list(self, test_client, url_prefix):
        """Test with large list of CIDs (near the 1000 limit)."""
        cids = list(range(1, 1001))  # 1000 CIDs exactly
        cids_str = ",".join(map(str, cids))

        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs={cids_str}"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert isinstance(data, list)

    def test_get_associated_substance_ids_too_many_cids(self, test_client, url_prefix):
        """Test error handling when exceeding the 1000 CID limit."""
        # Create a list of 1001 CIDs
        cids = list(range(1, 1002))
        cids_str = ",".join(map(str, cids))

        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs={cids_str}"
        )

        # Should return 400 error for exceeding limit
        assert response.status_code == 400

    def test_get_associated_substance_ids_database_parameter(
        self, test_client, url_prefix
    ):
        """Test with explicit database parameter."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=6&database=badapple_classic"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert isinstance(data, list)

    def test_get_associated_substance_ids_response_format(
        self, test_client, url_prefix
    ):
        """Test that response format matches expected structure exactly."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=6"
        )

        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()

        # Verify exact structure
        assert isinstance(data, list)
        if len(data) > 0:
            result = data[0]
            # Keys should be exactly "CID" and "SIDs"
            assert set(result.keys()) == {"CID", "SIDs"}
            assert isinstance(result["CID"], int)
            assert isinstance(result["SIDs"], list)
            # All SIDs should be integers
            for sid in result["SIDs"]:
                assert isinstance(sid, int)

    def test_get_associated_substance_ids_duplicate_cids(self, test_client, url_prefix):
        """Test behavior with duplicate CIDs in request."""
        response = test_client.get(
            f"{url_prefix}/compound_search/get_associated_substance_ids?CIDs=6,6,6"
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should only return one result for CID 6, not duplicates
        assert isinstance(data, list)
        if len(data) > 0:
            cids_in_response = [item["CID"] for item in data]
            assert cids_in_response.count(6) == 1
