import pytest
from unittest.mock import MagicMock, patch
from psycopg2.sql import SQL, Identifier, Placeholder
from viixoo_core.models.postgres import PostgresModel
from viixoo_core.models.domain import DomainTranslator
from typing import Optional


class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"

    id: int
    name: Optional[str] = None
    value: Optional[int] = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestPostgresModelQueryUpdate:

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_update_with_rows(self, mock_translate, mock_get_connection):
        """Test query_update method with rows."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_rows = [{"name": "Updated Test 1", "value": 20}]
        mock_domain = [("id", "=", 1)]
        mock_where_clause = "WHERE id = %s"
        mock_params = [1]
        mock_translate.return_value = (mock_where_clause, mock_params)
        mock_result = [{"id": 1}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        results = model.query_update(rows=mock_rows, domain=mock_domain)

        # Assert
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once_with(mock_domain)
        mock_cursor.execute.assert_called_once()
        assert results == mock_result

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_update_no_rows(self, mock_translate, mock_get_connection):
        """Test query_update method with no rows, use model_dump."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_domain = [("id", "=", 1)]
        mock_where_clause = "WHERE id = %s"
        mock_params = [1]
        mock_translate.return_value = (mock_where_clause, mock_params)
        mock_result = [{"id": 1}]
        mock_cursor.fetchall.return_value = mock_result

        model = MockPostgresModel(id=1, name="Test", value=10)

        # Act
        results = model.query_update(domain=mock_domain)

        # Assert
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once_with(mock_domain)
        mock_cursor.execute.assert_called_once()
        assert results == mock_result
        
    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_update_error(self, mock_translate, mock_get_connection):
        """Test query_update method when an error occurs."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_rows = [{"name": "Updated Test 1", "value": 20}]
        mock_domain = [("id", "=", 1)]
        mock_translate.return_value = ("WHERE id = %s", [1])
        mock_cursor.execute.side_effect = Exception("Some error")

        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(Exception) as e:
            model.query_update(rows=mock_rows, domain=mock_domain)
        assert "Some error" in str(e.value)
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once()
        mock_cursor.execute.assert_called_once()
