import pytest
from unittest.mock import patch, mock_open
import os
from viixoo_core.config import BaseConfig


class TestBaseConfig:

    @patch.dict('os.environ', clear=True)
    def test_from_env(self):
        """Test from_env method."""
        # Arrange
        os.environ["test_module_DB_TYPE"] = "sqlite"
        os.environ["test_module_DB_NAME"] = "test_db"
        os.environ["test_module_DB_USER"] = "test_user"
        os.environ["test_module_DB_PASSWORD"] = "test_password"
        os.environ["test_module_DB_HOST"] = "test_host"
        os.environ["test_module_DB_PORT"] = "1234"

        # Act
        config = BaseConfig.from_env("test_module")

        # Assert
        assert config["db_type"] == "sqlite"
        assert config["dbname"] == "test_db"
        assert config["user"] == "test_user"
        assert config["password"] == "test_password"
        assert config["host"] == "test_host"
        assert config["port"] == 1234

    @patch.dict('os.environ', clear=True)
    def test_from_env_defaults(self):
        """Test from_env method with default values."""
        # Act
        config = BaseConfig.from_env("test_module")

        # Assert
        assert config["db_type"] is False
        assert config["dbname"] == "viixoo_app_engine_test_db"
        assert config["user"] == "postgres"
        assert config["password"] == ""
        assert config["host"] == "localhost"
        assert config["port"] == 5432

    @patch("builtins.open", new_callable=mock_open, read_data="[database]\ndb_type=postgresql\ndbname=test_db\nuser=test_user\npassword=test_password\nhost=test_host\nport=1234")
    @patch("os.path.exists")
    def test_from_file_success(self, mock_exists, mock_open):
        """Test from_file method with a valid file."""
        # Arrange
        mock_exists.return_value = True

        # Act
        config = BaseConfig.from_file("test_module/test_module.conf")

        # Assert
        assert config["db_type"] == "postgresql"
        assert config["dbname"] == "test_db"
        assert config["user"] == "test_user"
        assert config["password"] == "test_password"
        assert config["host"] == "test_host"
        assert config["port"] == 1234        

    @patch("os.path.exists")
    def test_from_file_not_found(self, mock_exists):
        """Test from_file method when the file is not found."""
        # Arrange
        mock_exists.return_value = False

        # Act & Assert
        with pytest.raises(FileNotFoundError) as e:
            BaseConfig.from_file("test_module/test_module.conf")
        assert "Config file not found: test_module/test_module.conf" in str(e.value)

    @patch.object(BaseConfig, "from_env")
    @patch.object(BaseConfig, "from_file")
    @patch("os.path.join")
    @patch("os.path.exists")
    def test_get_config_from_env(self, mock_exists, mock_join, mock_from_file, mock_from_env, capsys):
        """Test get_config method with environment variables."""
        # Arrange
        mock_from_env.return_value = {"db_type": "sqlite", "dbname": "env_db", "user": "env_user", "password": "env_password", "host": "env_host", "port": 1111}
        mock_from_file.return_value = {"db_type": "postgresql", "dbname": "file_db", "user": "file_user", "password": "file_password", "host": "file_host", "port": 2222}
        mock_join.return_value = "/test/path/test_module/test_module.conf"
        mock_exists.return_value = True

        # Act
        config = BaseConfig.get_config("/test/path", "test_module")

        # Assert
        mock_from_env.assert_called_once_with(module="test_module")
        mock_from_file.assert_not_called()
        mock_join.assert_not_called()
        mock_exists.assert_not_called()
        assert config == {"db_type": "sqlite", "dbname": "env_db", "user": "env_user", "password": "env_password", "host": "env_host", "port": 1111}

    @patch.object(BaseConfig, "from_env")
    @patch.object(BaseConfig, "from_file")
    @patch("os.path.join")
    @patch("os.path.exists")
    def test_get_config_from_file(self, mock_exists, mock_join, mock_from_file, mock_from_env, capsys):
        """Test get_config method with a .conf file."""
        # Arrange
        mock_from_env.return_value = {"db_type": False, "dbname": "env_db", "user": "env_user", "password": "env_password", "host": "env_host", "port": 1111}
        mock_from_file.return_value = {"db_type": "postgresql", "dbname": "file_db", "user": "file_user", "password": "file_password", "host": "file_host", "port": 2222}
        mock_join.return_value = "/test/path/test_module/test_module.conf"
        mock_exists.return_value = True

        # Act
        config = BaseConfig.get_config("/test/path", "test_module")
        captured = capsys.readouterr()

        # Assert
        mock_from_env.assert_called_once_with(module="test_module")
        mock_from_file.assert_called_once_with("/test/path/test_module/test_module.conf")
        mock_join.assert_called_once_with("/test/path", "test_module", "test_module.conf")
        assert config == {"db_type": "postgresql", "dbname": "file_db", "user": "file_user", "password": "file_password", "host": "file_host", "port": 2222}
        assert "📂 Config from file: /test/path/test_module/test_module.conf" in captured.out

