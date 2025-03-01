from unittest.mock import patch
from viixoo_core.models.postgres import PostgresModel
from typing import Optional


class MockPostgresModel(PostgresModel):
    __tablename__ = "mock_table"

    
    id: int
    name: Optional[str] = None
    value: Optional[int] = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestPostgresModelSearch:

    @patch.object(PostgresModel, "query_select")
    def test_search_with_domain(self, mock_query_select):
        """Test search method with a domain."""
        # Arrange
        mock_domain = [("name", "=", "Test")]
        mock_result = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test"}]
        mock_query_select.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        results = model.search(domain=mock_domain)

        # Assert
        mock_query_select.assert_called_once_with(mock_domain, limit=0, offset=0)
        assert results == mock_result

    @patch.object(PostgresModel, "query_select")
    def test_search_no_domain(self, mock_query_select):
        """Test search method with no domain."""
        # Arrange
        mock_result = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]
        mock_query_select.return_value = mock_result

        model = MockPostgresModel(id=1)

        # Act
        results = model.search()

        # Assert
        mock_query_select.assert_called_once_with([], limit=0, offset=0)
        assert results == mock_result


class TestPostgresModelSearchLoad:

    @patch.object(PostgresModel, "query_select")
    def test_search_load_with_domain(self, mock_query_select):
        """Test search_load method with a domain."""
        # Arrange
        mock_domain = [("name", "=", "Test")]
        mock_query_results = [{"id": 1, "name": "Test", "value": 10}, {"id": 2, "name": "Test", "value": 20}]
        mock_query_select.return_value = mock_query_results
        model = MockPostgresModel(id=1)

        # Act
        results = model.search_load(domain=mock_domain)

        # Assert
        mock_query_select.assert_called_once_with(mock_domain)
        assert len(results) == 2
        assert isinstance(results[0], MockPostgresModel)
        assert results[0].id == 1
        assert results[0].name == "Test"
        assert results[0].value == 10
        assert isinstance(results[1], MockPostgresModel)
        assert results[1].id == 2
        assert results[1].name == "Test"
        assert results[1].value == 20

    @patch.object(PostgresModel, "query_select")
    def test_search_load_no_domain(self, mock_query_select):
        """Test search_load method with no domain."""
        # Arrange
        mock_query_results = [{"id": 1, "name": "Test1", "value": 10}, {"id": 2, "name": "Test2", "value": 20}]
        mock_query_select.return_value = mock_query_results
        model = MockPostgresModel(id=1)

        # Act
        results = model.search_load()

        # Assert
        mock_query_select.assert_called_once_with([])
        assert len(results) == 2
        assert isinstance(results[0], MockPostgresModel)
        assert results[0].id == 1
        assert results[0].name == "Test1"
        assert results[0].value == 10
        assert isinstance(results[1], MockPostgresModel)
        assert results[1].id == 2
        assert results[1].name == "Test2"
        assert results[1].value == 20