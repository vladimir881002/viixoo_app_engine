import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier
from viixoo_core.models.postgres import PostgresModel
from viixoo_core.models.base import BaseDBModel
from viixoo_core.models.domain import DomainTranslator
from typing import List, Dict, Any

class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestPostgresModelQueryDelete:

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_delete_success(self, mock_translate, mock_get_connection):
        """Test query_delete method successfully."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_domain = [("id", "=", 1)]
        mock_where_clause = "WHERE id = %s"
        mock_params = [1]
        mock_translate.return_value = (mock_where_clause, mock_params)

        model = MockPostgresModel(id=1)

        # Act
        result = model.query_delete(domain=mock_domain)

        # Assert
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once_with(mock_domain)
        assert result is True

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_delete_no_domain(self, mock_translate, mock_get_connection):
        """Test query_delete method with no domain (should raise ValueError)."""
        # Arrange
        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(ValueError) as e:
            model.query_delete(domain=[])
        assert "Domain is required to delete rows." in str(e.value)
        mock_get_connection.assert_not_called()
        mock_translate.assert_not_called()

    @patch.object(PostgresModel, "get_connection")
    @patch.object(DomainTranslator, "translate")
    def test_query_delete_error(self, mock_translate, mock_get_connection):
        """Test query_delete method when an error occurs."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mock_domain = [("id", "=", 1)]
        mock_where_clause = "WHERE id = %s"
        mock_params = [1]
        mock_translate.return_value = (mock_where_clause, mock_params)
        mock_cursor.execute.side_effect = Exception("Some error")

        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(Exception) as e:
            model.query_delete(domain=mock_domain)
        assert "Some error" in str(e.value)
        mock_get_connection.assert_called_once()
        mock_translate.assert_called_once()
        mock_cursor.execute.assert_called_once()
