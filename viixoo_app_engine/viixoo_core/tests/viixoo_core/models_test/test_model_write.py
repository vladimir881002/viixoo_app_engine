import pytest
from unittest.mock import patch
from viixoo_core.models.postgres import PostgresModel


class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestPostgresModelWrite:

    @patch.object(PostgresModel, "query_update")
    def test_write_with_rows_and_domain(self, mock_query_update):
        """Test write method with rows and a domain."""
        # Arrange
        mock_rows = [{"name": "Updated Test 1", "value": 20}]
        mock_domain = [("id", "=", 1)]
        mock_result = [{"id": 1}]
        mock_query_update.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        result = model.write(rows=mock_rows, domain=mock_domain)
        assert result == mock_result

    @patch.object(PostgresModel, "query_update")
    def test_write_no_rows_with_domain(self, mock_query_update):
        """Test write method with no rows but with a domain."""
        # Arrange
        mock_domain = [("id", "=", 1)]
        mock_result = [{"id": 1}]
        mock_query_update.return_value = mock_result
        model = MockPostgresModel(id=1, name="Test", value=10)

        # Act
        result = model.write(rows=[], domain=mock_domain)
        assert result == mock_result

    @patch.object(PostgresModel, "query_update")
    def test_write_with_rows_no_domain(self, mock_query_update):
        """Test write method with rows and no domain."""
        # Arrange
        mock_rows = [{"name": "Updated Test 1", "value": 20}]
        mock_domain = [('id', '=', 1)]
        mock_result = [{"id": 1}]
        mock_query_update.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        result = model.write(rows=mock_rows)
        assert result == mock_result

    @patch.object(PostgresModel, "query_update")
    def test_write_no_rows_no_domain(self, mock_query_update):
        """Test write method with no rows and no domain."""
        # Arrange
        mock_result = [{"id": 1}]
        mock_query_update.return_value = mock_result

        model = MockPostgresModel(id=1, name="Test", value=10)

        # Act
        result = model.write()

        # Assert
        assert result == mock_result

    @patch.object(PostgresModel, "query_update")
    def test_write_error(self, mock_query_update):
        """Test write method error."""
        # Arrange
        mock_rows = [{"name": "Updated Test 1", "value": 20}]
        mock_domain = [("id", "=", 1)]
        mock_query_update.side_effect = Exception("Some error")

        model = MockPostgresModel()

        # Act
        with pytest.raises(Exception) as e:
            model.write(rows=mock_rows, domain=mock_domain)
        assert "Some error" in str(e.value)
