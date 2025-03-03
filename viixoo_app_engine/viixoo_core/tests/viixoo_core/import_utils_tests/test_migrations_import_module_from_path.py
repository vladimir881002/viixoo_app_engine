from unittest.mock import MagicMock, patch
from viixoo_core.import_utils import ImportUtils
import sys


class TestMigrationImportModuleFromPath:

    @patch('viixoo_core.import_utils.importlib.util.spec_from_file_location')
    @patch('viixoo_core.import_utils.importlib.util.module_from_spec')
    @patch('viixoo_core.import_utils.os.path.exists')
    @patch('viixoo_core.import_utils.os.path.isdir')
    @patch('viixoo_core.import_utils.os.listdir')
    def test_import_module_from_path_success(self, mock_listdir, mock_isdir, mock_exists, mock_module_from_spec, mock_spec_from_file_location):
        """Test import_module_from_path successfully imports modules."""
        # Arrange
        mock_listdir.return_value = ["valid_package1", "not_a_package", "valid_package2", "file.txt"]
        mock_isdir.side_effect = lambda x: True if "valid_package" in x else False
        mock_exists.side_effect = lambda x: True if "__init__.py" in x else False

        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        # Act
        modules = ImportUtils.import_module_from_path('/test/path/')

        # Assert
        assert len(modules) == 2
        assert modules["valid_package1"] == mock_module
        assert modules["valid_package2"] == mock_module
        mock_spec_from_file_location.assert_called()
        mock_module_from_spec.assert_called()
        mock_spec.loader.exec_module.assert_called()
        mock_listdir.assert_called_once_with('/test/path/')
        assert mock_isdir.call_count == 4
        assert mock_exists.call_count == 2
        assert "valid_package1" in sys.modules
        assert "valid_package2" in sys.modules

    @patch('viixoo_core.import_utils.os.listdir')
    def test_import_module_from_path_file_not_found(self, mock_listdir, capsys):
        """Test import_module_from_path when the directory is not found."""
        # Arrange
        mock_listdir.side_effect = FileNotFoundError

        # Act
        modules = ImportUtils.import_module_from_path('/non/existent/path/')

        # Assert
        assert modules == {}
        captured = capsys.readouterr()
        assert "🚨 Module directory '/non/existent/path/' not found." in captured.out
        mock_listdir.assert_called_once_with('/non/existent/path/')

    @patch('viixoo_core.import_utils.os.listdir')
    def test_import_module_from_path_general_error(self, mock_listdir, capsys):
        """Test import_module_from_path when a general error occurs."""
        # Arrange
        mock_listdir.side_effect = Exception("Some error")

        # Act
        modules = ImportUtils.import_module_from_path('/test/path/')

        # Assert
        assert modules == {}
        captured = capsys.readouterr()
        assert "❌ Error loading plugins: Some error" in captured.out
        mock_listdir.assert_called_once_with('/test/path/')
    
    @patch('viixoo_core.import_utils.importlib.util.spec_from_file_location')
    @patch('viixoo_core.import_utils.os.path.exists')
    @patch('viixoo_core.import_utils.os.path.isdir')
    @patch('viixoo_core.import_utils.os.listdir')
    def test_import_module_from_path_no_spec(self, mock_listdir, mock_isdir, mock_exists, mock_spec_from_file_location):
        """Test import_module_from_path when spec_from_file_location returns None."""
        # Arrange
        mock_listdir.return_value = ["package1"]
        mock_isdir.return_value = True
        mock_exists.return_value = True
        mock_spec_from_file_location.return_value = None
    
        # Act
        modules = ImportUtils.import_module_from_path('/test/path/')
    
        # Assert
        assert len(modules) == 0
        mock_spec_from_file_location.assert_called_once()
    
    @patch('viixoo_core.import_utils.importlib.util.spec_from_file_location')
    @patch('viixoo_core.import_utils.importlib.util.module_from_spec')
    @patch('viixoo_core.import_utils.os.path.exists')
    @patch('viixoo_core.import_utils.os.path.isdir')
    @patch('viixoo_core.import_utils.os.listdir')
    def test_import_module_from_path_no_module(self, mock_listdir, mock_isdir, mock_exists, mock_module_from_spec, mock_spec_from_file_location):
        """Test import_module_from_path when module_from_spec returns None."""
        # Arrange
        mock_listdir.return_value = ["package1"]
        mock_isdir.return_value = True
        mock_exists.return_value = True
        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec
        mock_module_from_spec.return_value = None
    
        # Act
        modules = ImportUtils.import_module_from_path('/test/path/')
    
        # Assert
        assert len(modules) == 0
        mock_module_from_spec.assert_called_once()
        mock_spec_from_file_location.assert_called_once()
