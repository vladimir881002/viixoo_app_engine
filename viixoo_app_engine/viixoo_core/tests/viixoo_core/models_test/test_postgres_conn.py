import pytest
from unittest.mock import MagicMock, patch
import viixoo_core
from viixoo_core.models.postgres import PostgresModel
from viixoo_core.models.domain import DomainTranslator
from viixoo_core.config import BaseConfig
from psycopg2.sql import SQL, Identifier
import importlib


class TestPostgresModelGetConnection:

    @patch.object(BaseConfig, "get_config")
    @patch("psycopg2.connect")
    @patch.object(importlib, "import_module")
    def test_get_connection_new_connection(self, mock_import_module, mock_psycopg2_connect, mock_get_config):
        """Test get_connection when a new connection is required."""
        # Arrange
        mock_config = {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "test_host",
            "port": 5432
        }
        mock_get_config.return_value = mock_config

        mock_module = MagicMock()
        mock_module.__path__ = ["/test/path"]
        mock_import_module.return_value = mock_module

        mock_connection = MagicMock()
        mock_psycopg2_connect.return_value = mock_connection
        viixoo_core.models.postgres.db_connection = mock_connection

        model = PostgresModel(id=1)
        model.__class__.__module__ = "test_module.models"

        # Act
        connection = model.get_connection()

        # Assert
        assert connection == mock_connection
        mock_import_module.assert_called_once_with("test_module")
        mock_get_config.assert_called_once_with(base_path="/test/path", module="models")
        mock_psycopg2_connect.assert_called_once_with(
            **mock_config
        )

        # Clean up
        viixoo_core.models.postgres.db_connection = False

    @patch("psycopg2.connect")
    def test_get_connection_existing_connection(self, mock_psycopg2_connect):
        """Test get_connection when an existing connection is available and open."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.closed = False
        viixoo_core.models.postgres.db_connection = mock_connection
        model = PostgresModel(id=1)

        # Act
        connection = model.get_connection()

        # Assert
        assert connection == mock_connection
        mock_psycopg2_connect.assert_not_called()

        # Clean up
        viixoo_core.models.postgres.db_connection = False

    @patch.object(BaseConfig, "get_config")
    @patch("psycopg2.connect")
    @patch.object(importlib, "import_module")
    def test_get_connection_existing_connection_closed(self, mock_import_module, mock_psycopg2_connect, mock_get_config):
        """Test get_connection when an existing connection is available but closed."""
        # Arrange
        mock_config = {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "test_host",
            "port": 5432
        }
        mock_get_config.return_value = mock_config

        mock_connection_closed = MagicMock()
        mock_connection_closed.closed = True
        viixoo_core.models.postgres.db_connection = mock_connection_closed

        mock_module = MagicMock()
        mock_module.__path__ = ["/test/path"]
        mock_import_module.return_value = mock_module

        mock_connection_new = MagicMock()
        mock_psycopg2_connect.return_value = mock_connection_new

        model = PostgresModel(id=1)
        # Act
        connection = model.get_connection()

        # Assert
        assert connection == mock_connection_new
        mock_psycopg2_connect.assert_called_once_with(**mock_config)

        # Clean up
        viixoo_core.models.postgres.db_connection = False

    @patch.object(BaseConfig, "get_config")
    @patch("psycopg2.connect")
    @patch.object(importlib, "import_module")
    def test_get_connection_error(self, mock_import_module, mock_psycopg2_connect, mock_get_config):
        """Test get_connection error."""
        # Arrange
        mock_get_config.side_effect = Exception("Some error")

        mock_module = MagicMock()
        mock_module.__path__ = ["/test/path"]
        mock_import_module.return_value = mock_module

        mock_connection = MagicMock()
        mock_psycopg2_connect.return_value = mock_connection

        model = PostgresModel(id=1)
        model.__class__.__module__ = "test_module.models"

        # Act
        with pytest.raises(Exception) as e:
            model.get_connection()
        assert "Some error" in str(e.value)

        # Assert
        mock_import_module.assert_called_once_with("test_module")
        mock_get_config.assert_called_once_with(base_path="/test/path", module="models")
        mock_psycopg2_connect.assert_not_called()
