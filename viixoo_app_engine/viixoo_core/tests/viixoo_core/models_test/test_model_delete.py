import pytest
from unittest.mock import patch
from viixoo_core.models.postgres import PostgresModel


class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestPostgresModelDelete:

    @patch.object(PostgresModel, "query_delete")
    def test_delete_success(self, mock_query_delete):
        """Test delete method successfully."""
        # Arrange
        mock_query_delete.return_value = True
        mock_domain = [("id", "=", 1)]
        model = MockPostgresModel(id=1)

        # Act
        result = model.delete(domain=mock_domain)

        # Assert
        mock_query_delete.assert_called_once_with(mock_domain)
        assert result is True

    @patch.object(PostgresModel, "query_delete")
    def test_delete_no_domain(self, mock_query_delete):
        """Test delete method with no domain (should raise ValueError)."""
        # Arrange
        model = MockPostgresModel(id=1)

        # Act & Assert
        with pytest.raises(ValueError) as e:
            model.delete(domain=[])
        assert "Domain is required to delete rows." in str(e.value)
        mock_query_delete.assert_not_called()
