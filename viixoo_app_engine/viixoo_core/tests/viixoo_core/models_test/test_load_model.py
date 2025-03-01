from unittest.mock import patch
from viixoo_core.models.postgres import PostgresModel


class TestPostgresModelLoadModel:

    @patch.object(PostgresModel, "query_select")
    def test_load_model(self, mock_query_select):
        """Test load_model method."""
        # Arrange
        mock_query_results = [
            {"id": 1, "name": "Test 1"},
            {"id": 2, "name": "Test 2"},
        ]
        mock_query_select.return_value = mock_query_results

        class MockModel(PostgresModel):
            __tablename__ = "mock_table"
            id: int
            name: str

        model = MockModel(id=1, name="Fake name")
        # Act
        loaded_models = model.load_model()

        # Assert
        mock_query_select.assert_called_once_with([])
        assert len(loaded_models) == 2
        assert isinstance(loaded_models[0], MockModel)
        assert loaded_models[0].id == 1
        assert loaded_models[0].name == "Test 1"
        assert loaded_models[1].id == 2
        assert loaded_models[1].name == "Test 2"
