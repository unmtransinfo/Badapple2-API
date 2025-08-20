"""
@author Jack Ringer
Date: 8/20/2025
Description:
Tests for BadAppleSession class to verify database connectivity
and basic functionality.
"""

from unittest.mock import MagicMock, patch

import psycopg2
import pytest
from database.badapple import BadAppleSession


class TestBadAppleSession:
    """Test suite for BadAppleSession class."""

    @pytest.fixture(params=["badapple_classic", "badapple2"])
    def db_name(self, request):
        """Parameterized fixture to test both databases."""
        return request.param

    def test_context_manager_connection(self, db_name):
        """Test that BadAppleSession can connect to database using context manager."""
        try:
            with BadAppleSession(db_name) as session:
                # Verify connection is established
                connection = session.connection
                cursor = session.cursor
                assert connection is not None
                assert cursor is not None
                assert not connection.closed

                # Test a simple query to verify connection works
                session.cursor.execute("SELECT 1 as test_value;")
                result = session.cursor.fetchone()
                assert result["test_value"] == 1

            # After exiting context, connection should be closed
            assert connection.closed != 0  # psycopg2 uses non-zero for closed
            assert cursor.closed != 0

        except psycopg2.OperationalError as e:
            pytest.skip(f"Could not connect to {db_name} database: {e}")

    def test_multiple_queries_same_session(self, db_name):
        """Test that multiple queries can be executed within the same session."""
        try:
            with BadAppleSession(db_name) as session:
                # Execute multiple test queries
                session.cursor.execute("SELECT 1 as first_query;")
                result1 = session.cursor.fetchone()

                session.cursor.execute("SELECT 2 as second_query;")
                result2 = session.cursor.fetchone()

                assert result1["first_query"] == 1
                assert result2["second_query"] == 2

        except psycopg2.OperationalError as e:
            pytest.skip(f"Could not connect to {db_name} database: {e}")

    def test_invalid_db_name(self):
        """Test behavior with invalid database name."""
        # This should raise a KeyError when trying to access config values
        with pytest.raises(KeyError):
            with BadAppleSession("invalid_db_name") as session:
                pass


class TestBadAppleSessionMethods:
    """Test specific methods of BadAppleSession (with mocked database)."""

    @pytest.fixture
    def mock_session(self):
        """Create a mocked BadAppleSession for testing methods."""
        with patch("database.badapple.psycopg2.connect"):
            session = BadAppleSession("badapple2")
            session.connection = MagicMock()
            session.cursor = MagicMock()
            return session

    def test_execute_query_builder_success(self, mock_session):
        """Test successful query execution through _execute_query_builder."""

        # Mock query builder
        def mock_query_builder(arg):
            return f"SELECT * FROM test WHERE id = {arg}"

        # Mock cursor fetchall return
        mock_session.cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        result = mock_session._execute_query_builder(mock_query_builder, 1)

        assert result == [{"id": 1, "name": "test"}]
        mock_session.cursor.execute.assert_called_once()
        mock_session.cursor.fetchall.assert_called_once()

    def test_execute_query_builder_with_error_handler(self, mock_session):
        """Test _execute_query_builder with error handler."""

        def mock_query_builder(arg):
            raise psycopg2.errors.DataException("Invalid data")

        def mock_error_handler(e):
            return "Error handled"

        result = mock_session._execute_query_builder(
            mock_query_builder, "invalid", error_handler=mock_error_handler
        )

        assert result == "Error handled"


class TestIntegration:
    """Integration tests that require actual database connectivity."""

    def test_real_database_scaffold_search(self):
        """Test actual scaffold search if database is available."""
        try:
            with BadAppleSession("badapple2") as session:
                result = session.search_scaffold_by_smiles("c1ccncc1")  # pyridine
                assert isinstance(result, list)
        except psycopg2.OperationalError:
            pytest.skip("Database not available for integration test")
        except Exception as e:
            if "relation" in str(e) and "does not exist" in str(e):
                pytest.skip("Database schema not set up for integration test")
            else:
                raise

    def test_real_database_table_existence(self):
        """Test that expected tables exist in the databases."""
        shared_tables = ["scaffold", "compound", "sub2cpd", "scaf2cpd"]
        badapple2_tables = [
            "scaf2drug",
            "scaf2activeaid",
            "aid2target",
            "target",
        ]  # additional tables for badapple2 queries

        for db_name in ["badapple_classic", "badapple2"]:
            try:
                with BadAppleSession(db_name) as session:
                    expected_tables = (
                        shared_tables
                        if db_name == "badapple_classic"
                        else shared_tables + badapple2_tables
                    )
                    for table in expected_tables:
                        # Check if table exists
                        session.cursor.execute(
                            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
                            (table,),
                        )
                        exists = session.cursor.fetchone()["exists"]
                        assert exists, f"Table {table} does not exist in {db_name}"

            except psycopg2.OperationalError:
                pytest.skip(f"Database {db_name} not available for integration test")
