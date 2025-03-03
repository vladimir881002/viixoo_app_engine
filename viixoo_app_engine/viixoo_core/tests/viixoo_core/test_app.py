import unittest
from unittest.mock import patch, MagicMock
from fastapi.routing import APIRoute
from viixoo_core.app import load_modules, app, controller, API_PREFIX
from viixoo_core.import_utils import APPS_PATH
# This is needed for running app test
from starlette.testclient import TestClient


class TestApp:
    @patch("viixoo_core.app.ImportUtils.import_module_from_path")
    def test_load_modules_success(self, mock_import_module):
        """Test load_modules function with successful module loading."""

        # Mock the return value of import_module_from_path
        mock_module_1 = MagicMock()
        mock_module_1.routes.routes = MagicMock()
        mock_module_1.routes.routes.register_routes = MagicMock()

        mock_module_2 = MagicMock()
        mock_module_2.routes.routes = MagicMock()
        mock_module_2.routes.routes.register_routes = MagicMock()

        mock_modules = {"module1": mock_module_1, "module2": mock_module_2}
        mock_import_module.return_value = mock_modules

        # Call the function
        load_modules()

        # Assertions
        mock_import_module.assert_called_once_with(APPS_PATH)
        mock_module_1.routes.routes.register_routes.assert_called_once_with(
            controller
        )
        mock_module_2.routes.routes.register_routes.assert_called_once_with(
            controller
        )

    @patch("viixoo_core.app.ImportUtils.import_module_from_path")
    def test_load_modules_no_routes(self, mock_import_module, capsys):
        """Test load_modules when a module has no routes attribute."""

        # Mock the return value of import_module_from_path
        mock_module_1 = MagicMock()
        mock_module_1.routes = MagicMock()
        mock_module_1.routes.routes = None

        mock_modules = {"module1": mock_module_1}
        mock_import_module.return_value = mock_modules

        # Call the function
        load_modules()

        # Assertions
        mock_import_module.assert_called_once_with(APPS_PATH)
        captured = capsys.readouterr()
        assert " don't have routes, ignoring..." in captured.out

    @patch("viixoo_core.app.ImportUtils.import_module_from_path")
    def test_load_modules_no_register_routes(self, mock_import_module, capsys):
        """Test load_modules when a module has no register_routes method."""

        # Mock the return value of import_module_from_path
        mock_module_1 = MagicMock()
        mock_module_1.routes = MagicMock()
        mock_module_1.routes.routes = MagicMock()
        mock_module_1.routes.routes.register_routes = None

        mock_modules = {"module1": mock_module_1}
        mock_import_module.return_value = mock_modules

        # Call the function
        load_modules()

        # Assertions
        captured = capsys.readouterr()
        mock_import_module.assert_called_once_with(APPS_PATH)
        assert "Error loading modules" in captured.out
    
    @patch("viixoo_core.app.ImportUtils.import_module_from_path")
    def test_load_modules_error(self, mock_import_module):
        """Test load_modules function with an exception during module loading."""

        # Mock import_module_from_path to raise an exception
        mock_import_module.side_effect = Exception("Test exception")

        # Call the function
        load_modules()

        # Assertions
        mock_import_module.assert_called_once_with(APPS_PATH)

    def test_app_endpoints(self):
        """Test the main app endpoints (healthcheck, /, /v1, /v1/docs)."""

        client = TestClient(app)

        # Healthcheck
        response = client.get(f"{API_PREFIX}/healthcheck")
        assert response.status_code == 200
        assert response.text == '"OK"'

        # / (redirect to docs)
        response = client.get("/")
        assert response.history[0].status_code == 307
        assert  response.history[0].headers["location"] == f"{API_PREFIX}/docs"

        # /v1 (redirect to docs)
        response = client.get("/v1")
        assert response.history[0].status_code == 307
        assert response.history[0].headers["location"] == f"{API_PREFIX}/docs"

        # /v1/docs (swagger)
        response = client.get(f"{API_PREFIX}/docs")
        assert response.status_code == 200
        assert "Swagger UI" in response.text

    def test_app_has_router(self):
        """Check if the main app has the APIRouter"""
        routers = [r for r in app.routes if isinstance(r, APIRoute)]
        assert len(routers) > 0
