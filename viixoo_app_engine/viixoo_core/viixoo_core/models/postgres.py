import psycopg2
import importlib
from psycopg2.extras import RealDictCursor
from psycopg2.sql import Identifier, SQL, Placeholder
from .base import BaseDBModel
from typing import Dict, Any, List
from ..config import BaseConfig
from .domain import DomainTranslator

db_connection = False


class PostgresModel(BaseDBModel):
    """Modelo base para PostgreSQL."""

    def get_connection(self):
        global db_connection

        if db_connection and not db_connection.closed:
            return db_connection
        # Get the package name where the model is defined
        package_name = self.__class__.__module__.split('.')

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
            port=config["port"]
        )
        return connection
    
    def load_model(self, model_class: BaseDBModel, domain: List[Any] = []) -> List[BaseDBModel]:
        """Load a model from the database. ``domain`` is a list of tuples, each
        containing a field name, an operator and a value. For example::
            [('name', '=', 'John'), ('age', '>', 30)]
        """
        query_results = self.query_select(domain)
        return [model_class(**query_result) for query_result in query_results]
            
    def query_select(self, columns: List[str] = False, domain: List[Any] = []) -> List[Dict]:
        where_clause, params = DomainTranslator.translate(domain)
        query = SQL("SELECT {fields} FROM {table} {where_clause}").format(
            fields=SQL(", ").join(map(Identifier, columns)) if columns else SQL("*"),
            table=Identifier(self.__tablename__),
            where_clause=SQL(where_clause),
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
            
    def query_insert(self, rows: List[Dict]) -> List[Dict]:
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

    def query_update(self, rows: List[Dict], domain: List[Any]) -> List[Dict]:
        where_clause, params = DomainTranslator.translate(domain)
        setters = set(rows[0].keys())
        query = SQL("UPDATE {table} SET {assignment} {where_clause} RETURNING id").format(
            table=Identifier(self.__tablename__),
            assignment=SQL(", ").join(
                SQL("{} = {}").format(Identifier(s), Placeholder(s))
                for s in setters
            ),
            where_clause=SQL(where_clause),
        )
        values = [[row[col] for col in setters] for row in rows]
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values + params)
                return cur.fetchall()
            
    def query_delete(self, domain: List[Any]) -> bool:
        where_clause, params = DomainTranslator.translate(domain)
        query = SQL("DELETE FROM {table} {where_clause}").format(
            table=Identifier(self.__tablename__),
            where_clause=SQL(where_clause),
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return True
    
    def write(self, rows: List[Dict], domain: List[Any]) -> List[int]:
        """ 
            Write the given rows to the table. If the table has a primary key, it
            will be used to update existing rows
        """
        if not rows:
            return []
        return self.query_update(rows, domain)
    
    def create(self, rows: List[Dict]) -> BaseDBModel:
        """ 
            Create the given rows to the table. Return a list of models created.
        """
        ids = self.query_insert(rows)
        domain = [('id', '=', id_['id']) for id_ in ids]
        return self.load_model(self.__class__, domain)[0]
    
    def search(self, domain: List[Any] = []) -> List[Dict[str, Any]]:
        """
            Read the given rows from the table. Filter by domain. If no domain is given, return all rows.
        """
        query_results = self.query_select(domain)
        return query_results
    
    def delete(self, domain: List[Any] = []) -> bool:
        return self.query_delete(domain)
