"""Test the run method of the Migration class."""

import pytest
from unittest.mock import MagicMock, patch
from viixoo_core.migrations import Migration
from viixoo_core.import_utils import ImportUtils
from viixoo_core.config import BaseConfig


class TestMigrationRun:
    """Test the run method of the Migration class."""

    @patch.object(ImportUtils, "import_module_from_path")
    @patch.object(BaseConfig, "get_config")
    @patch.object(Migration, "run_postgresql_migrations")
    def test_run_postgresql(
        self,
        mock_run_postgresql_migrations,
        mock_get_config,
        mock_import_module,
        capsys,
    ):
        """Test run method with PostgreSQL database."""
        # Arrange
        mock_import_module.return_value = {
            "module1": MagicMock(),
            "module2": MagicMock(),
        }
        mock_get_config.side_effect = [
            {
                "db_type": "postgresql",
                "user": "user1",
                "password": "password1",
                "host": "host1",
                "port": "port1",
                "dbname": "dbname1",
            },
            {
                "db_type": "postgresql",
                "user": "user2",
                "password": "password2",
                "host": "host2",
                "port": "port2",
                "dbname": "dbname2",
            },
        ]

        # Act
        Migration.run()

        # Assert
        assert mock_import_module.call_count == 1
        assert mock_get_config.call_count == 2
        assert mock_run_postgresql_migrations.call_count == 2
        captured = capsys.readouterr()
        assert "🚀 Migrations completed for module module1" in captured.out
        assert "🚀 Migrations completed for module module2" in captured.out
        assert "✅ Migrations completed." in captured.out

    @patch.object(ImportUtils, "import_module_from_path")
    @patch.object(BaseConfig, "get_config")
    def test_run_unsupported_db(self, mock_get_config, mock_import_module):
        """Test run method with an unsupported database type."""
        # Arrange
        mock_import_module.return_value = [{"module1": MagicMock()}]
        mock_get_config.return_value = {"db_type": "sqlite"}

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            Migration.run()
        assert "Unsupported database engine: sqlite" in str(excinfo.value)
        mock_import_module.assert_called_once()
        mock_get_config.assert_called_once()

    @patch.object(ImportUtils, "import_module_from_path")
    @patch.object(BaseConfig, "get_config")
    @patch.object(Migration, "run_postgresql_migrations")
    def test_run_module_exception(
        self, mock_run_postgresql_migrations, mock_get_config, mock_import_module
    ):
        """Test run method when a module raise an exception."""
        # Arrange
        mock_import_module.side_effect = Exception("Some error")
        mock_get_config.return_value = {
            "db_type": "postgresql",
            "user": "user1",
            "password": "password1",
            "host": "host1",
            "port": "port1",
            "dbname": "dbname1",
        }
        mock_run_postgresql_migrations.return_value = None

        # Act
        with pytest.raises(Exception) as e:
            Migration.run()
        assert "Some error" in str(e.value)

        # Assert
        assert mock_import_module.call_count == 1
        assert mock_get_config.call_count == 0
        mock_run_postgresql_migrations.assert_not_called()

    @patch.object(ImportUtils, "import_module_from_path")
    @patch.object(BaseConfig, "get_config")
    @patch.object(Migration, "run_postgresql_migrations")
    def test_run_no_modules(
        self,
        mock_run_postgresql_migrations,
        mock_get_config,
        mock_import_module,
        capsys,
    ):
        """Test run method when no modules are found."""
        mock_import_module.return_value = {}

        # Act
        Migration.run()

        # Assert
        mock_import_module.assert_called_once()
        mock_get_config.assert_not_called()
        mock_run_postgresql_migrations.assert_not_called()
        captured = capsys.readouterr()
        assert "✅ Migrations completed." in captured.out
