import pytest
from unittest.mock import MagicMock, patch
from viixoo_core.migrations import Migration
from viixoo_core.models.base import BaseDBModel
from types import ModuleType
from typing import Optional
from datetime import date, datetime
from pydantic import Field



class MockBaseDBModel(BaseDBModel):
    __tablename__ = "mock_table"


class TestMigrationGetPostgresqlTables:
    class Model1(MockBaseDBModel):
            __tablename__ = "table1"

            # Add some fields to test the schema generation
            id: int
            name: str
            age: int
            is_active: bool
            date_field: Optional[date] = None
            datetime_field: Optional[datetime] = None
            str_field: Optional[str] = Field(max_length=255, json_schema_extra=dict(track_changes=True))
            str_unique_field: Optional[str] = Field(max_length=255, json_schema_extra=dict(unique=True))
            str_default_field: Optional[str] = Field(default="default_value")
            foreign_key: Optional[int] = Field(json_schema_extra=dict(foreign_key="example(id)", on_delete="SET NULL", on_update="CASCADE"))

    class Model2(MockBaseDBModel):
        __tablename__ = "table2"

    @patch.object(Migration, "pydantic_to_sql")
    def test_get_postgresql_tables_success(self, mock_pydantic_to_sql):
        """Test get_postgresql_tables function when models are correctly found."""
        # Arrange
        mock_module = MagicMock(spec=ModuleType)
        
        mock_module.Model1 = self.Model1
        mock_module.Model2 = self.Model2
        mock_module.__name__ = "test_module"

        mock_pydantic_to_sql.side_effect = lambda x: {"schema": f"schema_{x.__tablename__}"}

        # Act
        tables = Migration.get_postgresql_tables(mock_module)

        # Assert
        assert "table1" in tables
        assert "table2" in tables
        assert tables["table1"]["schema"] == "schema_table1"
        assert tables["table2"]["schema"] == "schema_table2"
        mock_pydantic_to_sql.assert_any_call(self.Model1)
        mock_pydantic_to_sql.assert_any_call(self.Model2)    
        assert mock_pydantic_to_sql.call_count == 2

    def test_get_postgresql_tables_module_not_found(self):
        """Test get_postgresql_tables function when a module is not found."""
        # Arrange
        mock_module = MagicMock(spec=ModuleType)
        mock_module.__name__ = "non_existent_module"

        # Mock dir function to raise ModuleNotFoundError when called
        with patch('builtins.dir', side_effect=ModuleNotFoundError):
          # Act & Assert
          with pytest.raises(ModuleNotFoundError):
              Migration.get_postgresql_tables(mock_module)

    def test_get_postgresql_tables_general_error(self):
        """Test get_postgresql_tables function when a general error occurs."""
        # Arrange
        mock_module = MagicMock(spec=ModuleType)
        mock_module.__name__ = "error_module"

        # Mock dir to raise a generic Exception
        with patch('builtins.dir', side_effect=Exception("Some error")):
            # Act & Assert
            with pytest.raises(Exception) as e:
                Migration.get_postgresql_tables(mock_module)
            assert "Some error" in str(e.value)

    def test_get_postgresql_tables_no_basemodel(self):
        # Arrange
        mock_module = MagicMock(spec=ModuleType)
        mock_module.__name__ = "error_module"

        class Model3:
            pass

        class Model4(object):
            pass

        mock_module.Model3 = Model3
        mock_module.Model4 = Model4

        # Act
        tables = Migration.get_postgresql_tables(mock_module)
        # Assert
        assert len(tables) == 0