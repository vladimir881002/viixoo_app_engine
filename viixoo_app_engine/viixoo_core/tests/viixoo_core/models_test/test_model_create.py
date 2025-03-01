import pytest
from unittest.mock import MagicMock, patch
from viixoo_core.models.postgres import PostgresModel
from typing import Optional


class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"

    id: int
    name: Optional[str] = None
    value: Optional[int] = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestPostgresModelCreate:

    @patch.object(PostgresModel, "query_insert")
    @patch.object(PostgresModel, "load_model")
    def test_create_with_rows(self, mock_load_model, mock_query_insert):
        """Test create method with rows."""
        # Arrange
        mock_rows = [{"name": "Test 1", "value": 10}, {"name": "Test 2", "value": 20}]
        mock_ids = [{"id": 1}, {"id": 2}]
        mock_query_insert.return_value = mock_ids
        mock_loaded_model = MagicMock()
        mock_load_model.return_value = [mock_loaded_model]
        
        model = MockPostgresModel(id=1)

        # Act
        result = model.create(rows=mock_rows)

        # Assert
        mock_query_insert.assert_called_once_with(mock_rows)
        mock_load_model.assert_called_once()
        # check the parameter in load_model
        assert mock_load_model.call_args[0][0] == MockPostgresModel
        assert mock_load_model.call_args[0][1] == [('id', '=', 1), ('id', '=', 2)]
        assert result == mock_loaded_model
    
    @patch.object(PostgresModel, "query_insert")
    @patch.object(PostgresModel, "load_model")
    def test_create_no_rows(self, mock_load_model, mock_query_insert):
        """Test create method with no rows (using model_dump)."""
        # Arrange
        mock_ids = [{"id": 1}]
        mock_query_insert.return_value = mock_ids
        mock_loaded_model = MagicMock()
        mock_load_model.return_value = [mock_loaded_model]
        model = MockPostgresModel(id=1, name="Test", value=10)

        # Act
        result = model.create(rows=[])

        # Assert
        mock_query_insert.assert_called_once_with([{'id': 1, 'name': 'Test', 'value': 10}])
        mock_load_model.assert_called_once()
        # check the parameter in load_model
        assert mock_load_model.call_args[0][0] == MockPostgresModel
        assert mock_load_model.call_args[0][1] == [('id', '=', 1)]
        assert result == mock_loaded_model

    @patch.object(PostgresModel, "query_insert")
    @patch.object(PostgresModel, "load_model")
    def test_create_error(self, mock_load_model, mock_query_insert):
        """Test create method error."""
        # Arrange
        mock_rows = [{"name": "Test 1", "value": 10}]
        mock_query_insert.side_effect = Exception("Some error")
        
        model = MockPostgresModel(id=1)

        # Act
        with pytest.raises(Exception) as e:
            model.create(rows=mock_rows)
        assert "Some error" in str(e.value)

        # Assert
        mock_query_insert.assert_called_once_with(mock_rows)
        mock_load_model.assert_not_called()
