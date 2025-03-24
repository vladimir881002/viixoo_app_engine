"""Base model class for all models in the application."""

import psycopg2
import importlib
from psycopg2.extras import RealDictCursor
from psycopg2.sql import Identifier, SQL, Placeholder
from typing import Dict, Any, List
from viixoo_core.models.base import BaseDBModel
from viixoo_core.models.domain import DomainTranslator
from viixoo_core.config import BaseConfig


db_connection = False


class PostgresModel(BaseDBModel):
    """PostgreSQL Base model."""

    def get_connection(self):
        """Get database connexion."""
        global db_connection

        if db_connection and not db_connection.closed:
            return db_connection
        # Get the package name where the model is defined
        package_name = self.__class__.__module__.split(".")

        module = importlib.import_module(package_name[0])

        # Get the base path of the package
        basepath = module.__path__[0]

        # Load the configuration for the package
        config = BaseConfig.get_config(base_path=basepath, module=package_name[1])

        # Establish the database connection using the configuration
        connection = psycopg2.connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )
        return connection

    def load_model(
        self, model_class: BaseDBModel = None, domain: List[Any] = []
    ) -> List[BaseDBModel]:
        """Load a model from the database.

        ``domain`` is a list of tuples, each
        containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]

        :param model_class: The class of the model to load
        :param domain: A list of tuples, each containing a field name, an operator and a value
        :return: A list of models loaded from the database
        """
        if not model_class:
            model_class = self.__class__

        query_results = self.query_select(domain)
        return [model_class(**query_result) for query_result in query_results]

    def query_select(
        self,
        columns: List[str] = False,
        domain: List[Any] = [],
        limit: int = 0,
        offset: int = 0,
    ) -> List[Dict]:
        """Select the given columns from the table. Filter by domain. If no domain is given, return all rows.

        :param columns: A list of column names to select
        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :param limit: The maximum number of rows to return
        :param offset: The number of rows to skip before returning rows
        :return: A list of dictionaries, each representing a row in the table
        """
        where_clause, params = DomainTranslator.translate(domain)
        query = SQL(
            "SELECT {fields} FROM {table} {where_clause} LIMIT {limit} OFFSET {offset}"
        ).format(
            fields=SQL(", ").join(map(Identifier, columns)) if columns else SQL("*"),
            table=Identifier(self.__tablename__),
            where_clause=SQL(where_clause) if where_clause else SQL(" 1=1 "),
            limit=SQL(limit) if limit != 0 else SQL("ALL"),
            offset=SQL(offset) if offset != 0 else SQL("0"),
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def query_insert(self, rows: List[Dict] = []) -> List[Dict]:
        """Insert the given rows into the table.

        :param rows: A list of dictionaries
        :return: A list of ids of the rows inserted
        """
        if not rows:
            rows = [self.model_dump()]

        cols = list(rows[0].keys())
        query = SQL("INSERT INTO {table} ({cols}) VALUES %s RETURNING id").format(
            table=Identifier(self.__tablename__),
            cols=SQL(", ").join(map(Identifier, cols)),
        )

        values = [[row[col] for col in cols] for row in rows]
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                return cur.fetchall()

    def query_update(self, rows: List[Dict] = [], domain: List[Any] = []) -> List[Dict]:
        """Update the given rows in the table. Filter by domain. If no domain is given, update all rows.

        :param rows: A list of dictionaries
        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :return: A list of ids of the rows updated
        """
        if not rows:
            rows = [self.model_dump()]

        params = []
        where_clause = ""

        if domain:
            where_clause, params = DomainTranslator.translate(domain)

        setters = set(rows[0].keys())
        query = SQL(
            "UPDATE {table} SET {assignment} {where_clause} RETURNING id"
        ).format(
            table=Identifier(self.__tablename__),
            assignment=SQL(", ").join(
                SQL("{} = {}").format(Identifier(s), Placeholder(s)) for s in setters
            ),
            where_clause=SQL(where_clause) if domain else SQL(" 1=1 "),
        )
        values = [[row[col] for col in setters] for row in rows]
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values + params)
                return cur.fetchall()

    def query_delete(self, domain: List[Any]) -> bool:
        """Delete the given rows from the table.

        Filter by domain. If no domain is given, raise a ValueError.

        :param domain: ``domain`` is a list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :return: True if the rows were deleted successfully, False otherwise
        """
        if not domain:
            raise ValueError("Domain is required to delete rows.")

        where_clause, params = DomainTranslator.translate(domain)
        query = SQL("DELETE FROM {table} {where_clause}").format(
            table=Identifier(self.__tablename__),
            where_clause=SQL(where_clause),
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return True

    def write(self, rows: List[Dict] = [], domain: List[Any] = []) -> List[int]:
        """Write the given rows to the table.

        If the table has a primary key, it will be used to update existing rows.

        :param rows: A list of dictionaries
        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :return: A list of ids of the rows written
        """
        if not rows:
            rows = [self.model_dump()]

        if not domain:
            domain = [("id", "=", self.id)]

        return self.query_update(rows, domain)

    def create(self, rows: List[Dict] = []) -> BaseDBModel:
        """
        Create the given rows to the table. Return a list of models created.

        :param rows: A list of dictionaries
        :return: A list of models created
        """
        if not rows:
            rows = [self.model_dump()]

        ids = self.query_insert(rows)
        domain = [("id", "=", id_["id"]) for id_ in ids]
        return self.load_model(self.__class__, domain)[0]

    def search(
        self, domain: List[Any] = [], limit: int = 0, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Read the given rows from the table. Filter by domain. If no domain is given, return all rows.

        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :param limit: The maximum number of rows to return
        :param offset: The number of rows to skip
        :return: A list of dictionaries
        """
        query_results = self.query_select(domain, limit=limit, offset=offset)
        return query_results

    def search_load(self, domain: List[Any] = []) -> List[BaseDBModel]:
        """
        Read the given rows from the table. Filter by domain. If no domain is given, return all rows.

        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :return: A list of models
        """
        query_results = self.query_select(domain)
        return [self.__class__(**query_result) for query_result in query_results]

    def delete(self, domain: List[Any]) -> bool:
        """Delete the given rows from the table. Filter by domain. If no domain is given, raise a ValueError.

        :param domain: A list of tuples, each containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        :return: True if the rows were deleted successfully, False otherwise
        """
        if not domain:
            raise ValueError("Domain is required to delete rows.")
        return self.query_delete(domain)
