from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from typing import Optional, Annotated


class BaseDBModel(BaseModel, ABC):
    """Abstract base class to handle multiple database engines."""

    __tablename__ = "table_name"  # Debe ser definido en cada modelo
    __description__ = "model_description"  # Debe ser definido en cada modelo
    __order__ = 'id'  # Debe ser definido en cada modelo

    id: Optional[Annotated[int, Field(json_schema_extra=dict(primary_key=True))]] = None

    @abstractmethod
    def get_connection(self):
        """Gets the database connection."""
        pass

    @abstractmethod
    def query_select(self, columns: List[str] = False, domain: List[Any] = []) -> List[Dict]:
        pass   

    @abstractmethod
    def query_insert(self, table: str, rows: dict) -> List[int]:
        """Inserts rows into a table."""
        pass

    @abstractmethod
    def query_update(self, table, values, selectors):
        """Updates rows in a table."""
        pass

    @abstractmethod
    def query_delete(self, table, selectors):
        """Deletes rows from a table."""
        pass

    @abstractmethod
    def write(self, rows: List[Dict]):
        """ 
            Write the given rows to the table. If the table has a primary key, it
            will be used to update existing rows, otherwise they will be inserted and return the ids of the new rows.
        """
        pass

    @abstractmethod
    def create(self, rows: List[Dict]):    
        """ 
            Create the given rows to the table. Return the ids of the new rows.
        """
        pass

    @abstractmethod
    def delete(self, selectors: List[Dict]):
        """
            Delete rows from the table. Filter by selectors. If not selectors are given, delete all rows.
        """
        pass

    @abstractmethod
    def search(self, selectors: List[Dict]):
        """
            Search the given rows from the table. Filter by selectors. If not selectors are given, return all rows.
        """
        pass

    @abstractmethod
    def search_load(self, selectors: List[Dict]):
        """
            Search the given rows from the table. Filter by selectors. If not selectors are given, return all rows.
        """
        pass
