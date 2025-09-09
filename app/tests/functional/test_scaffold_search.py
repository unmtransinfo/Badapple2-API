"""
@author Jack Ringer
Date: 8/21/2025
Description:
Functional tests for scaffold_search blueprint endpoints.
Note here that I'm just checking that the structure of results fetched by the API is correct.
Verifying that the DBs themselves are "accurate" is part of the DB construction.
"""

import pytest
from tests.helpers import (
    validate_active_assay_details_keys,
    validate_compound_keys,
    validate_drug_keys,
    validate_scaffold_keys,
    validate_target_keys,
)


class ScaffoldSearchTestBase:
    """Base class for scaffold search endpoint tests which use scafid as input."""

    endpoint = None  # To be overridden by subclasses

    def build_url(self, url_prefix, **params):
        """Build URL with query parameters."""
        url = f"{url_prefix}/scaffold_search/{self.endpoint}"
        query_params = []
        for key, value in params.items():
            if value is not None:
                query_params.append(f"{key}={value}")
        if query_params:
            url += "?" + "&".join(query_params)
        return url

    def run_test(
        self, test_client, url_prefix, status_code=200, id_in_db=True, **params
    ):
        """Base test runner with common validation logic."""
        url = self.build_url(url_prefix, **params)
        response = test_client.get(url)
        assert response.status_code == status_code

        if status_code == 200:
            data = response.get_json()
            self.validate_response(data, id_in_db)

    def validate_response(self, data, id_in_db):
        """Validate response data - to be overridden by subclasses."""
        pass

    def test_valid_id(self, test_client, url_prefix):
        """Test with valid scaffold ID."""
        scafid = 1  # expect DB to have at least 1 scaffold
        self.run_test(test_client, url_prefix, scafid=scafid)

    def test_invalid_id(self, test_client, url_prefix):
        """Test with invalid scaffold ID format."""
        scafid = "adm"
        self.run_test(
            test_client, url_prefix, scafid=scafid, status_code=400, id_in_db=False
        )

    def test_id_not_in_db(self, test_client, url_prefix):
        """Test with scaffold ID not in database."""
        scafid = -1
        self.run_test(test_client, url_prefix, scafid=scafid, id_in_db=False)

    def test_missing_id(self, test_client, url_prefix):
        """Test with missing scaffold ID parameter."""
        self.run_test(test_client, url_prefix, status_code=400)


class TestGetScaffoldID:
    """Functional tests for get_scaffold_id endpoint."""

    def run_test(
        self, test_client, url_prefix, smiles=None, database=None, status_code=200
    ):
        """Test runner for get_scaffold_id endpoint."""
        url = f"{url_prefix}/scaffold_search/get_scaffold_id"
        params = []
        if smiles is not None:
            params.append(f"SMILES={smiles}")
        if database is not None:
            params.append(f"database={database}")
        if params:
            url += "?" + "&".join(params)

        response = test_client.get(url)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            assert isinstance(data, int) or data is None

    def test_get_scaffold_id_valid_scaffold(self, test_client, url_prefix):
        smiles = "O=c1[nH]c(=O)c2[nH]cnc2[nH]1"
        self.run_test(test_client, url_prefix, smiles=smiles)

    def test_get_scaffold_id_invalid_scaffold(self, test_client, url_prefix):
        smiles = "asdas"
        self.run_test(test_client, url_prefix, smiles=smiles, status_code=400)

    def test_get_scaffold_id_missing_smiles(self, test_client, url_prefix):
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_scaffold_id_database_parameter(self, test_client, url_prefix):
        smiles = "O=c1[nH]c(=O)c2[nH]cnc2[nH]1"
        self.run_test(
            test_client, url_prefix, smiles=smiles, database="badapple_classic"
        )


class TestGetScaffoldInfo(ScaffoldSearchTestBase):
    """Functional tests for get_scaffold_info endpoint."""

    endpoint = "get_scaffold_info"

    def validate_response(self, data, id_in_db):
        """Validate scaffold info response."""
        if id_in_db:
            assert isinstance(data, dict)
            validate_scaffold_keys(data)
        else:
            assert data is None

    def test_get_scaffold_info_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(
            test_client, url_prefix, scafid=scafid, database="badapple_classic"
        )


class TestGetAssociatedCompounds(ScaffoldSearchTestBase):
    """Functional tests for get_associated_compounds endpoint."""

    endpoint = "get_associated_compounds"

    def validate_response(self, data, id_in_db):
        """Validate associated compounds response."""
        assert isinstance(data, list)
        if not id_in_db:
            assert len(data) == 0
        for compound_dict in data:
            assert isinstance(compound_dict, dict)
            validate_compound_keys(compound_dict)

    def test_get_associated_compounds_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(
            test_client, url_prefix, scafid=scafid, database="badapple_classic"
        )


@pytest.mark.requires_activity
class TestGetAssociatedAssayIDs(ScaffoldSearchTestBase):
    """Functional tests for get_associated_assay_ids endpoint."""

    endpoint = "get_associated_assay_ids"

    def validate_response(self, data, id_in_db):
        """Validate associated assay IDs response."""
        assert isinstance(data, list)
        if not id_in_db:
            assert len(data) == 0
        for aid in data:
            assert isinstance(aid, int)

    def test_get_associated_assay_ids_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(test_client, url_prefix, scafid=scafid, database="badapple2")


class TestGetActiveTargets(ScaffoldSearchTestBase):
    """Functional tests for get_active_targets endpoint."""

    endpoint = "get_active_targets"

    def validate_response(self, data, id_in_db):
        """Validate active targets response."""
        assert isinstance(data, list)
        if not id_in_db:
            assert len(data) == 0
        for target_info in data:
            assert isinstance(target_info, dict)
            assert "aid" in target_info
            # not all assays have target information
            if "target_id" in target_info:
                validate_target_keys(target_info)
            else:
                assert len(target_info.keys()) == 1  # should only have "aid"

    def test_get_active_targets_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(test_client, url_prefix, scafid=scafid, database="badapple2")

    def test_get_active_targets_bad_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(
            test_client,
            url_prefix,
            scafid=scafid,
            database="badapple_classic",
            status_code=400,
        )


class TestGetActiveAssayDetails(ScaffoldSearchTestBase):
    """Functional tests for get_active_assay_details endpoint."""

    endpoint = "get_active_assay_details"

    def validate_response(self, data, id_in_db):
        """Validate active assay details response."""
        assert isinstance(data, list)
        if not id_in_db:
            assert len(data) == 0
        for d in data:
            assert isinstance(d, dict)
            assert "aid" in d
            validate_active_assay_details_keys(d)

    def test_get_active_assay_details_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(test_client, url_prefix, scafid=scafid, database="badapple2")

    def test_get_active_assay_details_bad_database_parameter(
        self, test_client, url_prefix
    ):
        scafid = 1
        self.run_test(
            test_client,
            url_prefix,
            scafid=scafid,
            database="badapple_classic",
            status_code=400,
        )


class TestGetAssociatedDrugs(ScaffoldSearchTestBase):
    """Functional tests for get_associated_drugs endpoint."""

    endpoint = "get_associated_drugs"

    def validate_response(self, data, id_in_db):
        """Validate associated drugs response."""
        assert isinstance(data, list)
        if not id_in_db:
            assert len(data) == 0
        for drug_info in data:
            validate_drug_keys(drug_info)

    def test_get_associated_drugs_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(test_client, url_prefix, scafid=scafid, database="badapple2")

    def test_get_associated_drugs_bad_database_parameter(self, test_client, url_prefix):
        scafid = 1
        self.run_test(
            test_client,
            url_prefix,
            scafid=scafid,
            database="badapple_classic",
            status_code=400,
        )
