"""
@author Jack Ringer
Date: 8/20/2025
Description:
Functional tests for compound_search blueprint endpoints.
Note here that I'm just checking that the structure of results fetched by the API is correct.
Verifying that the DBs themselves are "accurate" is part of the DB construction.
"""

from tests.helpers import validate_scaffold_keys


class TestGetAssociatedSubstanceIds:
    """Functional tests for get_associated_substance_ids endpoint."""

    # note: only functions which start with "test" are counted as tests when pytest is run
    def run_test(
        self,
        test_client,
        url_prefix,
        CIDs: str = None,
        database: str = None,
        status_code: int = 200,
    ):
        url = f"{url_prefix}/compound_search/get_associated_substance_ids"
        if CIDs is not None:
            url += f"?CIDs={CIDs}"
        if database is not None:
            url += f"&database={database}"
        response = test_client.get(url)
        data = None
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
            if len(data) > 0:
                # verify data structure
                result = data[0]
                # Keys should be exactly "CID" and "SIDs"
                assert set(result.keys()) == {"CID", "SIDs"}
                assert isinstance(result["CID"], int)
                assert isinstance(result["SIDs"], list)
                # All SIDs should be integers
                for sid in result["SIDs"]:
                    assert isinstance(sid, int)

                # verify that all returned CIDs were in input
                cids_in_input = [int(cid) for cid in CIDs.split(",")]
                cids_in_response = [item["CID"] for item in data]
                for cid in cids_in_response:
                    assert cid in cids_in_input
                    assert cids_in_response.count(cid) == 1

    def test_get_associated_substance_ids_multiple_cids(self, test_client, url_prefix):
        """Test with multiple CIDs in the request."""
        CIDs = "6,7,8"
        self.run_test(test_client, url_prefix, CIDs)

    def test_get_associated_substance_ids_nonexistent_cid(
        self, test_client, url_prefix
    ):
        """Test with CID that doesn't exist in database."""
        # PubChem does not use negative CIDs
        CIDs = "-1"
        self.run_test(test_client, url_prefix, CIDs)

    def test_get_associated_substance_ids_mixed_cids(self, test_client, url_prefix):
        """Test with mix of existing and non-existing CIDs."""
        CIDs = "6,-1"
        self.run_test(test_client, url_prefix, CIDs)

    def test_get_associated_substance_ids_missing_parameter(
        self, test_client, url_prefix
    ):
        """Test error handling when CIDs parameter is missing."""
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_associated_substance_ids_invalid_cid_format(
        self, test_client, url_prefix
    ):
        """Test error handling with invalid CID format."""
        CIDs = "abc,def"
        self.run_test(test_client, url_prefix, CIDs, status_code=400)

    def test_get_associated_substance_ids_empty_cids(self, test_client, url_prefix):
        """Test with empty CIDs parameter."""
        CIDs = ""
        self.run_test(test_client, url_prefix, CIDs, status_code=400)

    def test_get_associated_substance_ids_large_list(self, test_client, url_prefix):
        """Test with large list of CIDs (near the 1000 limit)."""
        CIDs_list = list(range(1, 1001))  # 1000 CIDs exactly
        CIDs = ",".join(map(str, CIDs_list))
        self.run_test(test_client, url_prefix, CIDs)

    def test_get_associated_substance_ids_too_many_cids(self, test_client, url_prefix):
        """Test error handling when exceeding the 1000 CID limit."""
        CIDs_list = list(range(1, 1002))
        CIDs = ",".join(map(str, CIDs_list))
        self.run_test(test_client, url_prefix, CIDs, status_code=400)

    def test_get_associated_substance_ids_database_parameter(
        self, test_client, url_prefix
    ):
        """Test with explicit database parameter."""
        CIDs = "6"
        self.run_test(test_client, url_prefix, CIDs, database="badapple_classic")


def validate_scaffold_data(scaffold_data: list, assert_not_processed: bool):
    assert isinstance(scaffold_data, list)
    if assert_not_processed:
        assert len(scaffold_data) == 0
    for d in scaffold_data:
        assert isinstance(d, dict)
        assert "in_db" in d.keys()
        assert "scafsmi" in d.keys()
        if d["in_db"]:
            validate_scaffold_keys(d)


class TestGetAssociatedScaffolds:
    """Functional tests for get_associated_scaffolds endpoint."""

    def run_test(
        self,
        test_client,
        url_prefix,
        smiles: str = None,
        max_rings: int = None,
        database: str = None,
        status_code: int = 200,
        all_smiles_valid: bool = True,
        assert_not_processed: bool = False,
    ):
        url = f"{url_prefix}/compound_search/get_associated_scaffolds"
        if smiles is not None:
            url += f"?SMILES={smiles}"
        if max_rings is not None:
            url += f"&max_rings={max_rings}"
        if database is not None:
            url += f"&database={database}"
        response = test_client.get(url)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            assert isinstance(data, dict)
            smiles_list = smiles.split(",")
            if all_smiles_valid:
                assert len(data) == len(smiles_list)
            else:
                # this API call ignores invalid SMILES - they are given no key
                assert len(data) < len(smiles_list)
            if len(data) > 0:
                # verify that all outputs were part of inputs
                smiles_list = smiles.split(",")
                for smiles_key in data:
                    assert smiles_key in smiles_list
                    # verify structure of scaffold data
                    validate_scaffold_data(data[smiles_key], assert_not_processed)

    def test_get_associated_scaffolds_single_smiles(self, test_client, url_prefix):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"
        self.run_test(test_client, url_prefix, smiles)

    def test_get_associated_scaffolds_multiple_smiles(self, test_client, url_prefix):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12,COc1cc2c(ccnc2cc1)C(O)C4CC(CC3)C(C=C)CN34,CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(=O)O"
        self.run_test(test_client, url_prefix, smiles)

    def test_get_associated_scaffolds_no_smiles(self, test_client, url_prefix):
        smiles = ""
        self.run_test(test_client, url_prefix, smiles, status_code=400)

    def test_get_associated_scaffolds_with_invalid_smiles(
        self, test_client, url_prefix
    ):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12,adadadss"
        self.run_test(test_client, url_prefix, smiles, all_smiles_valid=False)

    def test_get_associated_scaffolds_limit(self, test_client, url_prefix):
        smiles = ["CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"] * 1001
        self.run_test(test_client, url_prefix, smiles, status_code=400)

    def test_get_associated_scaffolds_missing_smiles(self, test_client, url_prefix):
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_associated_scaffolds_database_parameter(self, test_client, url_prefix):
        """Test with explicit database parameter."""
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"
        self.run_test(test_client, url_prefix, smiles, database="badapple_classic")

    def test_get_associated_scaffolds_max_rings_parameter(
        self, test_client, url_prefix
    ):
        """Test with explicit database parameter."""
        smiles = "Cn1cc(C2=C(c3cn(C4CCN(Cc5ccccn5)CC4)c4ccccc34)C(=O)NC2=O)c2ccccc21"  # has 5 ring systems
        self.run_test(
            test_client, url_prefix, smiles, max_rings=3, assert_not_processed=True
        )


class TestGetAssociatedScaffoldsOrdered:
    """Functional tests for get_associated_scaffolds_ordered endpoint."""

    def run_test(
        self,
        test_client,
        url_prefix,
        smiles: str = None,
        names: str = None,
        max_rings: int = None,
        database: str = None,
        status_code: int = 200,
        assert_not_processed: bool = False,
    ):
        url = f"{url_prefix}/compound_search/get_associated_scaffolds_ordered"
        if smiles is not None:
            url += f"?SMILES={smiles}"
        if names is not None:
            url += f"&Names={names}"
        if max_rings is not None:
            url += f"&max_rings={max_rings}"
        if database is not None:
            url += f"&database={database}"
        response = test_client.get(url)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.get_json()
            smiles_list = smiles.split(",")
            names_list = smiles_list
            if names:
                names_list = names.split(",")
            assert isinstance(data, list)
            assert len(data) == len(smiles_list)
            for i, entry in enumerate(data):
                assert entry["molecule_smiles"] == smiles_list[i]
                assert entry["name"] == names_list[i]
                scaffold_data = entry["scaffolds"]
                if scaffold_data is not None:
                    validate_scaffold_data(scaffold_data, assert_not_processed)
                else:
                    assert entry["error_msg"] == "Invalid SMILES, please check input"

    def test_get_get_associated_scaffolds_ordered_single_smiles(
        self, test_client, url_prefix
    ):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"
        self.run_test(test_client, url_prefix, smiles)

    def test_get_associated_scaffolds_ordered_multiple_smiles(
        self, test_client, url_prefix
    ):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12,COc1cc2c(ccnc2cc1)C(O)C4CC(CC3)C(C=C)CN34,CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(=O)O"
        self.run_test(test_client, url_prefix, smiles)

    def test_get_associated_scaffolds_ordered_no_smiles(self, test_client, url_prefix):
        smiles = ""
        self.run_test(test_client, url_prefix, smiles, status_code=400)

    def test_get_associated_scaffolds_ordered_with_invalid_smiles(
        self, test_client, url_prefix
    ):
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12,adadadss"
        self.run_test(test_client, url_prefix, smiles)

    def test_get_associated_scaffolds_ordered_limit(self, test_client, url_prefix):
        smiles = ["CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"] * 1001
        self.run_test(test_client, url_prefix, smiles, status_code=400)

    def test_get_associated_scaffolds_ordered_missing_smiles(
        self, test_client, url_prefix
    ):
        self.run_test(test_client, url_prefix, status_code=400)

    def test_get_associated_scaffolds_ordered_database_parameter(
        self, test_client, url_prefix
    ):
        """Test with explicit database parameter."""
        smiles = "CN1C(=O)N(C)C(=O)C(N(C)C=N2)=C12"
        self.run_test(test_client, url_prefix, smiles, database="badapple_classic")

    def test_get_associated_scaffolds_ordered_max_rings_parameter(
        self, test_client, url_prefix
    ):
        """Test with explicit database parameter."""
        smiles = "Cn1cc(C2=C(c3cn(C4CCN(Cc5ccccn5)CC4)c4ccccc34)C(=O)NC2=O)c2ccccc21"  # has 5 ring systems
        self.run_test(
            test_client, url_prefix, smiles, max_rings=3, assert_not_processed=True
        )
