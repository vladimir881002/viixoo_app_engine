"""Base class for database models."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from typing import Optional, Annotated


class BaseDBModel(BaseModel, ABC):
    """Abstract base class to handle multiple database engines."""

    __tablename__ = "table_name"  # Debe ser definido en cada modelo
    __description__ = "model_description"  # Debe ser definido en cada modelo
    __order__ = "id"  # Debe ser definido en cada modelo

    id: Optional[Annotated[int, Field(json_schema_extra=dict(primary_key=True))]] = None

    @abstractmethod
    def get_connection(self):
        """Get the database connection."""
        raise NotImplementedError("Subclasses must implement get_connection method.")

    @abstractmethod
    def query_select(
        self, columns: List[str] = False, domain: List[Any] = []
    ) -> List[Dict]:
        """Select rows from a table.

        :param columns: The columns to select
        :param domain: A list of tuples, each containing a field name, an operator and a value
        :return: A list of rows loaded from the database
        """
        raise NotImplementedError("Subclasses must implement query_select method.")

    @abstractmethod
    def query_insert(self, table: str, rows: dict) -> List[int]:
        """Insert rows into a table."""
        raise NotImplementedError("Subclasses must implement query_insert method.")

    @abstractmethod
    def query_update(self, table, values, selectors):
        """Update rows in a table."""
        raise NotImplementedError("Subclasses must implement query_update method.")

    @abstractmethod
    def query_delete(self, table, selectors):
        """Delete rows from a table."""
        raise NotImplementedError("Subclasses must implement query_delete method.")

    @abstractmethod
    def write(self, rows: List[Dict]):
        """Write the given rows to the table.

        If the table has a primary key, it will be used to update existing rows,
        otherwise they will be inserted and return the ids of the new rows.
        """
        raise NotImplementedError("Subclasses must implement write method.")

    @abstractmethod
    def create(self, rows: List[Dict]):
        """Create the given rows to the table. Return the ids of the new rows."""
        raise NotImplementedError("Subclasses must implement create method.")

    @abstractmethod
    def delete(self, selectors: List[Dict]):
        """Delete rows from the table. Filter by selectors. If not selectors are given, delete all rows."""
        raise NotImplementedError("Subclasses must implement delete method.")

    @abstractmethod
    def search(self, selectors: List[Dict]):
        """Search the given rows from the table. Filter by selectors. If not selectors are given, return all rows."""
        raise NotImplementedError("Subclasses must implement search method.")

    @abstractmethod
    def search_load(self, selectors: List[Dict]):
        """Search the given rows from the table. Filter by selectors. If not selectors are given, return all rows."""
        raise NotImplementedError("Subclasses must implement search_load method.")
