"""Tests for the query_select method of the PostgresModel class."""

import pytest
from unittest.mock import MagicMock, patch
from viixoo_core.models.postgres import PostgresModel
from viixoo_core.models.domain import DomainTranslator
from psycopg2.sql import SQL, Identifier


class MockPostgresModel(PostgresModel):
    """A mock class for testing the query_select method of the PostgresModel class."""

    __tablename__ = "mock_table"

    def __init__(self, *args, **kwargs):
        """Initialize the mock model."""
        super().__init__(*args, **kwargs)


class TestPostgresModelQuerySelect:
    """Tests for the query_select method of the PostgresModel class."""

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_select_no_columns_no_domain(
        self, mock_translate, mock_get_connection
    ):
        """Test query_select method with no columns and no domain."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_translate.return_value = ("", [])

        mock_result = [
            {"id": 1, "name": "Fake name 1"},
            {"id": 2, "name": "Fake name 2"},
        ]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1, name="Fake name")

        # Act
        results = model.query_select()
        expected_query = SQL(
            "SELECT {fields} FROM {table} {where_clause} LIMIT {limit} OFFSET {offset}"
        ).format(
            fields=SQL("*"),
            table=Identifier("mock_table"),
            where_clause=SQL(" 1=1 "),
            limit=SQL("ALL"),
            offset=SQL("0"),
        )

        # Assert
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once_with([])
        mock_cursor.execute.assert_called_once_with(expected_query, [])
        assert results == mock_result

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_select_with_columns_with_domain(
        self, mock_translate, mock_get_connection
    ):
        """Test query_select method with columns and domain."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_domain = [("name", "=", "Fake name")]
        mock_where = "WHERE name = %s"
        mock_params = ["Fake name"]
        mock_translate.return_value = (mock_where, mock_params)

        mock_columns = ["id", "name"]
        mock_result = [{"id": 1, "name": "Fake name"}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1, name="Fake name")
        # Act
        results = model.query_select(columns=mock_columns, domain=mock_domain)

        # Assert
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once_with(mock_domain)
        mock_cursor.execute.assert_called_once_with(
            SQL(
                "SELECT {fields} FROM {table} {where_clause} LIMIT {limit} OFFSET {offset}"
            ).format(
                fields=SQL(", ").join(map(Identifier, mock_columns)),
                table=Identifier("mock_table"),
                where_clause=SQL(mock_where),
                limit=SQL("ALL"),
                offset=SQL("0"),
            ),
            mock_params,
        )
        assert results == mock_result

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_select_error(self, mock_translate, mock_get_connection):
        """Test query_select method when an error occurs."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_translate.return_value = ("WHERE id = %s", [1])
        mock_cursor.execute.side_effect = Exception("Some error")

        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(Exception) as e:
            model.query_select()
        assert "Some error" in str(e.value)
        mock_get_connection.assert_called_once()
