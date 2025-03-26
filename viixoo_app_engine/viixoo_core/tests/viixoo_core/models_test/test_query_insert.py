"""Tests for the query_insert method of the PostgresModel class."""

import pytest
from unittest.mock import MagicMock, patch
from psycopg2.sql import SQL, Identifier
from viixoo_core.models.postgres import PostgresModel
from typing import Optional


class MockPostgresModel(PostgresModel):
    """A mock class for testing the query_insert method of the PostgresModel class."""

    __tablename__ = "mock_table"

    id: int
    name: Optional[str] = None
    value: Optional[int] = 0

    def __init__(self, *args, **kwargs):
        """Initialize the mock model."""
        super().__init__(*args, **kwargs)


class TestPostgresModelQueryInsert:
    """Tests for the query_insert method of the PostgresModel class."""

    @patch.object(PostgresModel, "get_connection")
    def test_query_insert_single_row(self, mock_get_connection):
        """Test query_insert method with a single row."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_rows = [{"name": "Test 1", "value": 10}]
        mock_result = [{"id": 1}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        results = model.query_insert(mock_rows)

        # Assert
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        assert results == mock_result
        assert mock_cursor.execute.call_args[0][1] == [["Test 1", 10]]
        # Check query
        expected_query = SQL(
            "INSERT INTO {table} ({cols}) VALUES %s RETURNING id"
        ).format(
            table=Identifier("mock_table"),
            cols=SQL(", ").join(map(Identifier, ["name", "value"])),
        )
        assert str(mock_cursor.execute.call_args[0][0]) == str(expected_query)

    @patch.object(PostgresModel, "get_connection")
    def test_query_insert_multiple_rows(self, mock_get_connection):
        """Test query_insert method with multiple rows."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_rows = [{"name": "Test 1", "value": 10}, {"name": "Test 2", "value": 20}]
        mock_result = [{"id": 1}, {"id": 2}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        results = model.query_insert(mock_rows)

        # Assert
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        assert results == mock_result
        # Check if the execute was called with multiple values
        assert mock_cursor.execute.call_args[0][1] == [["Test 1", 10], ["Test 2", 20]]
        # Check query
        expected_query = SQL(
            "INSERT INTO {table} ({cols}) VALUES %s RETURNING id"
        ).format(
            table=Identifier("mock_table"),
            cols=SQL(", ").join(map(Identifier, ["name", "value"])),
        )
        assert str(mock_cursor.execute.call_args[0][0]) == str(expected_query)

    @patch.object(PostgresModel, "get_connection")
    def test_query_insert_no_rows(self, mock_get_connection):
        """Test query_insert method without rows."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_result = [{"id": 1}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1, name="test", value=10)

        # Act
        results = model.query_insert()

        # Assert
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        assert results == mock_result
        # Check if the execute was called with multiple values
        assert mock_cursor.execute.call_args[0][1] == [[1, "test", 10]]
        # Check query
        expected_query = SQL(
            "INSERT INTO {table} ({cols}) VALUES %s RETURNING id"
        ).format(
            table=Identifier("mock_table"),
            cols=SQL(", ").join(map(Identifier, ["id", "name", "value"])),
        )
        assert str(mock_cursor.execute.call_args[0][0]) == str(expected_query)

    @patch.object(PostgresModel, "get_connection")
    def test_query_insert_error(self, mock_get_connection):
        """Test query_insert method when an error occurs."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_rows = [{"name": "Test 1", "value": 10}]
        mock_cursor.execute.side_effect = Exception("Some error")

        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(Exception) as e:
            model.query_insert(mock_rows)
        assert "Some error" in str(e.value)
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
