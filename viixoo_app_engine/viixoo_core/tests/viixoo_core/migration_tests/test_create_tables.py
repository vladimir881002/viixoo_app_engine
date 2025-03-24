"""Tests for the create_tables method in the Migration class."""

import unittest
from unittest.mock import patch, MagicMock
from psycopg2.extensions import connection as Connection
from viixoo_core.migrations import Migration


class TestMigration(unittest.TestCase):
    """Test the Migration class."""

    def setUp(self):
        """Set up the test and reset config."""
        Migration.config = {}

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query(self, mock_get_connection):
        """Test the generate_create_table_query method."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "name": {"type": "CHARACTER VARYING", "required": True, "unique": True},
            "age": {"type": "INTEGER", "required": False},
            "is_active": {"type": "BOOLEAN", "required": True},
            "category_id": {
                "type": "INTEGER",
                "foreign_key": "categories.id",
                "on_delete": "SET NULL",
                "on_update": "CASCADE",
            },
            "created_at": {
                "type": "TIMESTAMP WITHOUT TIME ZONE",
                "required": False,
                "default": "2023-01-01",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        expected_create_query = (
            "CREATE TABLE IF NOT EXISTS users (",
            "id SERIAL PRIMARY KEY, ",
            "name CHARACTER VARYING NOT NULL, ",
            "age INTEGER, ",
            "is_active BOOLEAN NOT NULL, ",
            "category_id INTEGER, ",
            "created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT '2023-01-01'::TIMESTAMP WITHOUT TIME ZONE, ",
            "CONSTRAINT name_unique UNIQUE (name));",
        )
        alter_table = """ ALTER TABLE users ADD CONSTRAINT category_id_fk"""
        references = """ FOREIGN KEY (category_id) REFERENCES categories.id"""
        polities_fk = """ ON DELETE SET NULL ON UPDATE CASCADE;"""
        expected_fk_query = f"""{alter_table}{references}{polities_fk}"""

        # Assertions
        for q in expected_create_query:
            self.assertIn(q, query)
        self.assertEqual(fk_query, expected_fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_no_fk(self, mock_get_connection):
        """Test the generate_create_table_query method without foreign keys."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "name": {"type": "CHARACTER VARYING", "required": True, "unique": True},
            "age": {"type": "INTEGER", "required": False},
            "is_active": {"type": "BOOLEAN", "required": True},
            "created_at": {
                "type": "TIMESTAMP WITHOUT TIME ZONE",
                "required": False,
                "default": "2023-01-01",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        c_fields = (
            "(id SERIAL PRIMARY KEY, name CHARACTER VARYING NOT NULL, age INTEGER, is_active BOOLEAN NOT NULL,"
            " created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT '2023-01-01'::TIMESTAMP WITHOUT TIME ZONE"
        )
        expected_create_query = f"CREATE TABLE IF NOT EXISTS users {c_fields}, CONSTRAINT name_unique UNIQUE (name));"

        expected_fk_query = ""

        # Assertions
        self.assertEqual(query, expected_create_query)
        self.assertEqual(fk_query, expected_fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_no_required(self, mock_get_connection):
        """Test the generate_create_table_query method without required fields."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "name": {"type": "CHARACTER VARYING", "required": False, "unique": True},
            "age": {"type": "INTEGER", "required": False},
            "is_active": {"type": "BOOLEAN", "required": False},
            "created_at": {
                "type": "TIMESTAMP WITHOUT TIME ZONE",
                "required": False,
                "default": "2023-01-01",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        c_fields = (
            "(id SERIAL PRIMARY KEY, name CHARACTER VARYING, age INTEGER, is_active BOOLEAN,"
            " created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT '2023-01-01'::TIMESTAMP WITHOUT TIME ZONE"
        )
        expected_create_query = f"CREATE TABLE IF NOT EXISTS users {c_fields}, CONSTRAINT name_unique UNIQUE (name));"

        expected_fk_query = ""

        # Assertions
        self.assertEqual(query, expected_create_query)
        self.assertEqual(fk_query, expected_fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_default(self, mock_get_connection):
        """Test the generate_create_table_query method with default fields."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "name": {
                "type": "CHARACTER VARYING",
                "required": False,
                "unique": True,
                "default": "test",
            },
            "age": {"type": "INTEGER", "required": False, "default": 18},
            "is_active": {"type": "BOOLEAN", "required": False, "default": False},
            "created_at": {
                "type": "TIMESTAMP WITHOUT TIME ZONE",
                "required": False,
                "default": "2023-01-01",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        expected_create_query1 = (
            "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,"
            " name CHARACTER VARYING DEFAULT 'test'::CHARACTER VARYING,"
        )
        expected_create_query2 = " age INTEGER DEFAULT '18'::INTEGER,"
        expected_create_query3 = " is_active BOOLEAN DEFAULT 'False'::BOOLEAN,"
        expected_create_query4 = " created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT '2023-01-01'::TIMESTAMP WITHOUT TIME ZONE,"
        expected_create_query5 = " CONSTRAINT name_unique UNIQUE (name));"
        expected_fk_query = ""

        # Assertions
        self.assertIn(expected_create_query1, query)
        self.assertIn(expected_create_query2, query)
        self.assertIn(expected_create_query3, query)
        self.assertIn(expected_create_query4, query)
        self.assertIn(expected_create_query5, query)
        self.assertEqual(fk_query, expected_fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_all_options(self, mock_get_connection):
        """Test the generate_create_table_query method with all field options."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "name": {
                "type": "CHARACTER VARYING",
                "required": True,
                "unique": True,
                "default": "test",
            },
            "age": {"type": "INTEGER", "required": True, "default": 18},
            "is_active": {"type": "BOOLEAN", "required": True, "default": False},
            "created_at": {
                "type": "TIMESTAMP WITHOUT TIME ZONE",
                "required": False,
                "default": "2023-01-01",
            },
            "category_id": {
                "type": "INTEGER",
                "foreign_key": "categories.id",
                "on_delete": "SET NULL",
                "on_update": "CASCADE",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        expected_create_query1 = (
            """CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,"""
        )
        expected_create_query2 = (
            """ name CHARACTER VARYING NOT NULL DEFAULT 'test'::CHARACTER VARYING,"""
        )
        expected_create_query3 = """ age INTEGER NOT NULL DEFAULT '18'::INTEGER,"""
        expected_create_query4 = (
            """ is_active BOOLEAN NOT NULL DEFAULT 'False'::BOOLEAN,"""
        )
        expected_create_query5 = """ created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT '2023-01-01'::TIMESTAMP WITHOUT TIME ZONE,"""
        expected_create_query6 = """ category_id INTEGER,"""
        expected_create_query7 = """ CONSTRAINT name_unique UNIQUE (name));"""

        expected_fk_query1 = """ ALTER TABLE users ADD CONSTRAINT category_id_fk"""
        expected_fk_query2 = """ FOREIGN KEY (category_id) REFERENCES categories.id ON DELETE SET NULL ON UPDATE CASCADE;"""

        # Assertions
        self.assertIn(expected_create_query1, query)
        self.assertIn(expected_create_query2, query)
        self.assertIn(expected_create_query3, query)
        self.assertIn(expected_create_query4, query)
        self.assertIn(expected_create_query5, query)
        self.assertIn(expected_create_query6, query)
        self.assertIn(expected_create_query7, query)

        self.assertIn(expected_fk_query1, fk_query)
        self.assertIn(expected_fk_query2, fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_no_on_delete(self, mock_get_connection):
        """Test the generate_create_table_query method without on_delete and on_update options."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "category_id": {
                "type": "INTEGER",
                "foreign_key": "categories.id",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        expected_create_query = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, category_id INTEGER);"
        alter_table = """ ALTER TABLE users ADD CONSTRAINT category_id_fk"""
        references = """ FOREIGN KEY (category_id) REFERENCES categories.id;"""
        expected_fk_query = f"""{alter_table}{references}"""

        # Assertions
        self.assertEqual(query, expected_create_query)
        self.assertEqual(fk_query, expected_fk_query)

    @patch("viixoo_core.migrations.Migration.get_postgresql_connection")
    def test_generate_create_table_query_no_on_update(self, mock_get_connection):
        """Test the generate_create_table_query method without on_update options."""
        mock_conn = MagicMock(spec=Connection)
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Define a simple schema
        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True},
            "category_id": {
                "type": "INTEGER",
                "foreign_key": "categories.id",
                "on_delete": "CASCADE",
            },
        }

        # Call the method
        table_name = "users"
        query, fk_query = Migration.generate_create_table_query(table_name, schema)

        # Expected SQL queries
        expected_create_query = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, category_id INTEGER);"
        alter_table = " ALTER TABLE users ADD CONSTRAINT category_id_fk"
        references = " FOREIGN KEY (category_id) REFERENCES categories.id"
        fk_polities = " ON DELETE CASCADE;"
        expected_fk_query = f"{alter_table}{references}{fk_polities}"

        # Assertions
        self.assertEqual(query, expected_create_query)
        self.assertEqual(fk_query, expected_fk_query)
