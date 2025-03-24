"""Test the BaseDBModel class."""

import pytest
from viixoo_core.models.base import BaseDBModel
from typing import List, Dict, Any


class TestBaseDBModel:
    """Test the BaseDBModel class."""

    def test_base_db_model_is_abstract(self):
        """Test that BaseDBModel is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseDBModel()

    def test_base_db_model_attributes(self):
        """Test that BaseDBModel has the correct attributes."""
        assert hasattr(BaseDBModel, "__tablename__")
        assert hasattr(BaseDBModel, "__description__")
        assert hasattr(BaseDBModel, "__order__")
        assert "id" in BaseDBModel.model_fields

    def test_base_db_model_methods(self):
        """Test that BaseDBModel has the correct abstract methods."""
        assert hasattr(BaseDBModel, "get_connection")
        assert hasattr(BaseDBModel, "query_select")
        assert hasattr(BaseDBModel, "query_insert")
        assert hasattr(BaseDBModel, "query_update")
        assert hasattr(BaseDBModel, "query_delete")
        assert hasattr(BaseDBModel, "write")
        assert hasattr(BaseDBModel, "create")
        assert hasattr(BaseDBModel, "delete")
        assert hasattr(BaseDBModel, "search")
        assert hasattr(BaseDBModel, "search_load")

        assert getattr(BaseDBModel, "get_connection").__isabstractmethod__
        assert getattr(BaseDBModel, "query_select").__isabstractmethod__
        assert getattr(BaseDBModel, "query_insert").__isabstractmethod__
        assert getattr(BaseDBModel, "query_update").__isabstractmethod__
        assert getattr(BaseDBModel, "query_delete").__isabstractmethod__
        assert getattr(BaseDBModel, "write").__isabstractmethod__
        assert getattr(BaseDBModel, "create").__isabstractmethod__
        assert getattr(BaseDBModel, "delete").__isabstractmethod__
        assert getattr(BaseDBModel, "search").__isabstractmethod__
        assert getattr(BaseDBModel, "search_load").__isabstractmethod__

    def test_base_db_model_cannot_be_instantiated(self):
        """Test that the abstract methods cannot be instanced."""

        class ConcreteModel(BaseDBModel):
            __tablename__ = "test_table"
            __description__ = "test_description"
            __order__ = "id"

            def get_connection(self):
                pass

            def query_select(
                self, columns: List[str] = False, domain: List[Any] = []
            ) -> List[Dict]:
                pass

            def query_insert(self, rows: List[Dict]) -> List[Dict]:
                pass

            def query_update(self, rows, domain):
                pass

            def query_delete(self, domain):
                pass

            def write(self, rows: List[Dict]):
                pass

            def create(self, rows: List[Dict]):
                pass

            def delete(self, domain: List[Any]):
                pass

            def search(self, domain: List[Any]):
                pass

            def search_load(self, domain: List[Any]):
                pass

        # Act - Assert
        model = ConcreteModel()
        model.get_connection()
        model.query_select()
        model.query_insert([])
        model.query_update([], [])
        model.query_delete([])
        model.write([])
        model.create([])
        model.delete([])
        model.search([])
        model.search_load([])
