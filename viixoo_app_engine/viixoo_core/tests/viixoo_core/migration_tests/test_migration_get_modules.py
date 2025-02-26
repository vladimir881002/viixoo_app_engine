from unittest.mock import patch
from viixoo_core.migrations import Migration, APPS_PATH
from viixoo_core.models.base import BaseDBModel
import importlib
import sys



class MockBaseDBModel(BaseDBModel):
    __tablename__ = "mock_table"


class TestMigrationGetModules:

    @patch('viixoo_core.migrations.pkgutil.iter_modules')
    def test_get_modules(self, mock_iter_modules, capsys):
        """Test get_modules function when modules are found."""
        # Arrange
        mock_iter_modules.return_value = [
            (None, 'module1', False),
            (None, 'module2', False),
            (None, 'module3', True)
        ]

        # Act
        modules = Migration.get_modules()

        # Assert
        assert modules == ['module1', 'module2', 'module3']
        captured = capsys.readouterr()
        assert "🔍 Searching for application modules..." in captured.out
        assert f"📂 Searching in path: {APPS_PATH}" in captured.out
        assert "📦 Module found: module1" in captured.out
        assert "📦 Module found: module2" in captured.out
        assert "📦 Module found: module3" in captured.out

    @patch('viixoo_core.migrations.pkgutil.iter_modules')
    @patch('viixoo_core.migrations.os.path.join')
    @patch('viixoo_core.migrations.os.path.dirname')
    def test_get_modules_custom_app_path(self, mock_dirname, mock_join, mock_iter_modules, capsys, monkeypatch):
        """Test get_modules with a custom APPS_PATH environment variable."""
        monkeypatch.setenv("APPS_PATH", "/custom/app/path")

        mock_iter_modules.return_value = [
            (None, 'module1', False)
        ]
        mock_dirname.return_value = "test_dirname"
        mock_join.return_value = "/custom/app/path"

        # Reload migrations to get new config
        importlib.reload(sys.modules['viixoo_core.migrations'])

        modules = Migration.get_modules()

        # Assert
        assert modules == ['module1']
        captured = capsys.readouterr()
        assert "🔍 Searching for application modules..." in captured.out
        assert "📂 APPS_PATH: /custom/app/path" in captured.out
        assert "📂 Searching in path: /custom/app/path" in captured.out
        #Reload migrations to get default config
        monkeypatch.delenv("APPS_PATH")
        importlib.reload(sys.modules['viixoo_core.migrations'])
    
    @patch('viixoo_core.migrations.pkgutil.iter_modules')
    def test_get_modules_no_modules(self, mock_iter_modules, capsys, monkeypatch):
        """Test get_modules function when no modules are found."""
        monkeypatch.setenv("APPS_PATH", "/custom/app/path")
        # Arrange
        mock_iter_modules.return_value = []

        # Act
        modules = Migration.get_modules()

        # Assert
        assert modules == []
        captured = capsys.readouterr()
        assert "🔍 Searching for application modules..." in captured.out
        assert f"📂 Searching in path: /custom/app/path" in captured.out
        assert "📦 Module found:" not in captured.out

        #Reload migrations to get default config
        monkeypatch.delenv("APPS_PATH")
        importlib.reload(sys.modules['viixoo_core.migrations'])
