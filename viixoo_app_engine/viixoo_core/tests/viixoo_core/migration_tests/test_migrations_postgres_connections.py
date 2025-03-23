"""Tests for the get_postgresql_connection method in the Migration class."""

from unittest.mock import MagicMock
from psycopg2.sql import Identifier, SQL
from viixoo_core.migrations import Migration
import viixoo_core
import viixoo_core.migrations


class TestMigrationGetPostgresqlConnection:
    """Tests for the get_postgresql_connection method in the Migration class."""

    config = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "port": "test_port",
        "dbname": "test_db",
    }

    def test_get_postgresql_connection_new_db(self):
        """Test get_postgresql_connection when the database does not exist and is created."""
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect = viixoo_core.migrations.psycopg2.connect = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        mock_cursor.fetchone.return_value = None  # Database does not exist

        viixoo_core.migrations.config = self.config

        # Act
        conn = Migration.get_postgresql_connection()

        # Assert
        mock_connect.assert_called()
        assert conn == mock_connection
        assert mock_connection.autocommit is True
        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("test_db",)
        )
        mock_cursor.execute.assert_called_with(
            SQL("CREATE DATABASE {}").format(Identifier("test_db"))
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        assert mock_connect.call_count == 2

    def test_get_postgresql_connection_existing_db(self):
        """Test get_postgresql_connection when the database already exists."""
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect = viixoo_core.migrations.psycopg2.connect = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        viixoo_core.migrations.db_connection = mock_connection.return_value = (
            mock_connection
        )

        mock_cursor.fetchone.return_value = [1]  # Database exists

        viixoo_core.migrations.config = self.config
        # Act
        conn = Migration.get_postgresql_connection()

        # Assert
        mock_connect.assert_called()
        assert conn == mock_connection
        assert mock_connection.autocommit is True
        mock_cursor.execute.assert_called_with(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("test_db",)
        )
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        assert mock_connect.call_count == 2

    def test_get_postgresql_connection_already_connected(self):
        """Test get_postgresql_connection when already connected and connection is not closed."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection.closed = False
        mock_connect = viixoo_core.migrations.psycopg2.connect = mock_connection
        viixoo_core.migrations.db_connection = mock_connection

        viixoo_core.migrations.config = self.config
        # Act
        conn = Migration.get_postgresql_connection()

        # Assert
        assert conn == mock_connection
        mock_connect.assert_not_called()

        # Reset after the test
        viixoo_core.migrations.db_connection = False

    def test_get_postgresql_connection_connection_closed(self):
        """Test get_postgresql_connection when already connected but connection is closed."""
        # Arrange
        mock_connection_old = MagicMock()
        mock_connect = viixoo_core.migrations.psycopg2.connect = MagicMock()
        mock_connection_old.closed = True
        viixoo_core.migrations.db_connection = mock_connection_old

        mock_connection_new = MagicMock()
        mock_connection_new.cursor.return_value.fetchone.return_value = [1]
        mock_connect.return_value = mock_connection_new

        viixoo_core.migrations.config = self.config
        # Act
        conn = Migration.get_postgresql_connection()
        # Assert
        assert conn == mock_connection_new
        mock_connect.assert_called()
        assert mock_connection_new.autocommit is True

        # Reset after the test
        viixoo_core.migrations.db_connection = False
