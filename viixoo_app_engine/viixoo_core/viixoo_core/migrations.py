"""Database migrations for PostgreSQL with Pydantic models."""

import psycopg2
from psycopg2.sql import Identifier, SQL
from viixoo_core.config import BaseConfig
from viixoo_core.models.base import BaseDBModel
from viixoo_core.import_utils import ImportUtils, APPS_PATH
from types import ModuleType
from pydantic_core._pydantic_core import PydanticUndefinedType

db_connection = False
config: dict = {}


class Migration:
    """Base class for database migration."""

    # Base methods

    @classmethod
    def run(cls):
        """Run the migrations."""
        global config
        modules = ImportUtils.import_module_from_path(APPS_PATH)
        for module in modules:
            config = BaseConfig.get_config(APPS_PATH, module)
            if config["db_type"] == "postgresql":
                cls.run_postgresql_migrations(config=config, module=modules[module])
            else:
                raise ValueError(f"Unsupported database engine: {config['db_type']}")
            print(f"🚀 Migrations completed for module {module}")
        print("✅ Migrations completed.")

    # PostgreSQL Migrations

    @classmethod
    def get_postgresql_connection(cls):
        """Get the connection to PostgreSQL."""
        global db_connection
        global config

        if db_connection and not db_connection.closed:
            return db_connection

        db_connection = psycopg2.connect(
            dbname="postgres",
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )
        db_connection.autocommit = True
        cursor = db_connection.cursor()

        # Check if the database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (config["dbname"],)
        )
        db_exists = cursor.fetchone()

        if not db_exists:
            # Create the database if it does not exist
            print(f"🚀 Creating database {config['dbname']}...")
            cursor.execute(
                SQL("CREATE DATABASE {}").format(Identifier(config["dbname"]))
            )

        cursor.close()
        db_connection.close()

        db_connection = psycopg2.connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )

        return db_connection

    @classmethod
    def run_postgresql_migrations(cls, config: dict, module: ModuleType):
        """Run migrations for PostgreSQL with change logs."""
        # Connect to the database
        print("🚀 Starting migrations...")
        try:
            conn = cls.get_postgresql_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print(f"✅ Connected to PostgreSQL: {record} database: {config['dbname']}")

        except psycopg2.Error as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")
            return

        # Create log tables if they do not exist
        cls.create_migration_log_tables(cursor)

        # Check unaccent extension
        cls.enable_unaccent_extension(cursor)

        tables = cls.get_postgresql_tables(module=module)
        try:
            for table, schema in tables.items():
                if cls.table_exists(cursor, table):
                    cls.update_table_schema(cursor, table, schema)
                else:
                    create_table_query = cls.generate_create_table_query(table, schema)
                    for query in create_table_query:
                        cursor.execute(query)
                    cls.log_change("CREATE TABLE", f"Table '{table}' created")

                # Enable data change tracking if any field requires it
                cls.enable_data_tracking(cursor, table, schema)
        except Exception as e:
            print(f"❌ Error during migrations: {e}")
            conn.rollback()
        else:
            conn.commit()
            cursor.close()
            conn.close()

    @classmethod
    def create_migration_log_tables(cls, cursor):
        """Create the log tables if they do not exist."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_logs (
                id SERIAL PRIMARY KEY,
                action VARCHAR(50),
                description TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_logs_data (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(255),
                column_name VARCHAR(255),
                old_value TEXT,
                new_value TEXT,
                change_type VARCHAR(10), -- INSERT, UPDATE, DELETE
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """
        )

    @classmethod
    def log_change(cls, action: str, description: str):
        """Log a change in the database structure."""
        conn = cls.get_postgresql_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO migration_logs (action, description) VALUES (%s, %s)
        """,
            (action, description),
        )
        conn.commit()
        print(f"📝 LOG: {action} - {description}")

    @classmethod
    def table_exists(cls, cursor, table_name: str) -> bool:
        """Check if the table already exists in PostgreSQL."""
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables WHERE table_name = %s
            )
        """,
            (table_name,),
        )
        return cursor.fetchone()[0]

    @classmethod
    def get_existing_columns(cls, cursor, table_name: str) -> dict:
        """Get the existing columns in a table with their types and constraints."""
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
        """,
            (table_name,),
        )

        return {
            row[0]: {"type": row[1].upper(), "required": (row[2] == "NO")}
            for row in cursor.fetchall()
        }

    @classmethod
    def add_foreign_key(
        cls,
        cursor,
        table_name: str,
        column: str,
        foreign_table: str,
        on_delete: str,
        on_update: str,
    ):
        """Add a foreign key with configurable ON DELETE and ON UPDATE policies.

        Supported values:
            CASCADE, SET NULL, RESTRICT, NO ACTION, SET DEFAULT
        """
        fk_name = f"{table_name}_{column}_fk"

        # Remove the foreign key if it already exists
        cursor.execute(
            f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = '{fk_name}' AND table_name = '{table_name}'
                ) THEN
                    ALTER TABLE {table_name} DROP CONSTRAINT {fk_name};
                END IF;
            END $$;
        """
        )

        # Create the new FOREIGN KEY with custom policies
        query = f"""ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}
            ON DELETE CASCADE ON UPDATE CASCADE;"""

        if on_delete and on_update:
            query = query.replace("ON DELETE CASCADE", f"ON DELETE {on_delete}")
            query = query.replace("ON UPDATE CASCADE", f"ON UPDATE {on_update}")
        elif on_delete:
            query = query.replace("ON DELETE CASCADE", f"ON DELETE {on_delete}")
        elif on_update:
            query = query.replace("ON UPDATE CASCADE", f"ON UPDATE {on_update}")

        cursor.execute(query)

        cls.log_change(
            "ADD FOREIGN KEY",
            f"Foreign key '{column}' -> '{foreign_table}.id' in '{table_name}' with ON DELETE {on_delete} and ON UPDATE {on_update}",
        )

    @classmethod
    def remove_foreign_key(cls, cursor, table_name: str, column: str):
        """Remove a foreign key if it is no longer in the model."""
        fk_name = f"{table_name}_{column}_fk"
        cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {fk_name};")
        cls.log_change(
            "REMOVE FOREIGN KEY", f"FK '{column}' removed from '{table_name}'"
        )

    @classmethod
    def get_existing_foreign_keys(cls, cursor, table_name: str):
        """Return a dictionary with the existing foreign keys in the table."""
        cursor.execute(
            f"""
            SELECT kcu.column_name, ccu.table_name AS foreign_table
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
        """
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    @classmethod
    def get_postgresql_tables(cls, module: ModuleType) -> dict:
        """Get the Pydantic models and Generate table schemas with foreign keys and unique constraints."""
        tables = {}

        try:
            # List all attributes and classes in the module
            for attr_name in dir(module):
                if attr_name.startswith("__"):
                    continue
                attribute = getattr(module, attr_name)

                for sub_attr in dir(attribute):
                    if sub_attr.startswith("__"):
                        continue

                    sub_attr = getattr(attribute, sub_attr)
                    if (
                        isinstance(sub_attr, type)
                        and issubclass(sub_attr, BaseDBModel)
                        and sub_attr is not BaseDBModel
                    ):
                        table_name = sub_attr.__tablename__
                        tables[table_name] = cls.pydantic_to_sql(sub_attr)
        except ModuleNotFoundError:
            print(f"🚨 Module {module}.models not found")
            raise  # Ignore modules without models.py
        except Exception as e:
            print(f"❌ Error in module {module}: {e}")
            raise
        return tables

    @classmethod
    def remove_obsolete_columns(
        cls, cursor, table_name: str, existing_columns: dict, schema: dict
    ):
        """Remove the columns that are no longer in the Pydantic models with logs."""
        for column in existing_columns:
            if column not in schema:
                cursor.execute(
                    f"ALTER TABLE {table_name} DROP COLUMN {column} CASCADE;"
                )
                cls.log_change(
                    "DROP COLUMN",
                    f"Obsolete column '{column}' removed in '{table_name}'",
                )

    @classmethod
    def pydantic_to_sql(cls, model: type[BaseDBModel]) -> dict:
        """Convert a Pydantic model to a PostgreSQL schema with validations."""
        field_mapping = {
            "str": "CHARACTER VARYING",
            "int": "INTEGER",
            "float": "REAL",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP WITHOUT TIME ZONE",
        }

        schema = {
            "id": {"type": "SERIAL PRIMARY KEY", "required": True}
        }  # Default autoincremental ID

        for field_name, field in model.model_fields.items():
            field_type = field.annotation
            is_required = field.is_required()
            is_unique = (
                field.json_schema_extra.get("unique", False)
                if field.json_schema_extra
                else False
            )
            primary_key = (
                field.json_schema_extra.get("primary_key", False)
                if field.json_schema_extra
                else False
            )
            foreign_key = (
                field.json_schema_extra.get("foreign_key", None)
                if field.json_schema_extra
                else None
            )
            track_changes = (
                field.json_schema_extra.get("track_changes", False)
                if field.json_schema_extra
                else False
            )
            default = (
                field.default
                if field.default
                and not isinstance(field.default, PydanticUndefinedType)
                else False
            )
            on_delete = (
                field.json_schema_extra.get("on_delete", False)
                if field.json_schema_extra
                else False
            )
            on_update = (
                field.json_schema_extra.get("on_update", False)
                if field.json_schema_extra
                else False
            )

            if isinstance(field_type, type):
                field_type_str = f"{field_type.__name__}"
            elif hasattr(field_type, "__args__"):
                # field: Optional[int] ...
                if field_type.__name__ == "Optional":
                    field_type_str = field_type.__args__[0].__name__
                    is_required = False
            else:
                field_type_str = "str"

            sql_type = field_mapping.get(field_type_str, "TEXT")
            schema[field_name] = {
                "type": sql_type,
                "primary_key": primary_key,
                "required": is_required,
                "unique": is_unique,
                "foreign_key": foreign_key,
                "track_changes": track_changes,
                "default": default,
            }

            if on_delete:
                schema[field_name]["on_delete"] = on_delete
            if on_update:
                schema[field_name]["on_update"] = on_update

        return schema

    @classmethod
    def generate_create_table_query(cls, table: str, schema: dict) -> tuple[str]:
        """Generate an SQL query to create a table with foreign keys and unique constraints."""
        columns = []
        constraints = []
        contraints_fk = []
        for col, props in schema.items():
            col_def = f"{col} {props['type']}"

            if props.get("primary_key"):
                constraints.append(f"PRIMARY KEY ({col})")

            elif props.get("required") and "PRIMARY KEY" not in col_def:
                col_def += " NOT NULL"

            if props.get("unique") and "PRIMARY KEY" not in col_def:
                constraints.append(f"CONSTRAINT {col}_unique UNIQUE ({col})")

            if props.get("foreign_key"):
                alter_table = (
                    f""" ALTER TABLE {table.strip()} ADD CONSTRAINT {col}_fk"""
                )
                references = (
                    f""" FOREIGN KEY ({col}) REFERENCES {props['foreign_key']}"""
                )
                fk_polities = " ON DELETE CASCADE ON UPDATE CASCADE"
                contraints_query = f"""{alter_table}{references}{fk_polities}"""

                if props.get("on_delete"):
                    contraints_query = contraints_query.replace(
                        "ON DELETE CASCADE", f"ON DELETE {props['on_delete']}"
                    )  # 🔥
                else:
                    contraints_query = contraints_query.replace(
                        " ON DELETE CASCADE", ""
                    )

                if props.get("on_update"):
                    contraints_query = contraints_query.replace(
                        "ON UPDATE CASCADE", f"ON UPDATE {props['on_update']}"
                    )  # 🔥
                else:
                    contraints_query = contraints_query.replace(
                        " ON UPDATE CASCADE", ""
                    )

                contraints_fk.append(contraints_query + ";")

            if props.get("default", None) is not None and not props.get(
                "primary_key", None
            ):
                col_def += f" DEFAULT '{props['default']}'::{props['type']}"

            columns.append(col_def)

        query = (
            f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns + constraints)});"
        )
        return (query, "".join(contraints_fk))

    @classmethod
    def update_table_schema(cls, cursor, table_name: str, schema: dict):
        """Detect and apply any changes in the table schema with logs."""
        existing_columns = cls.get_existing_columns(cursor, table_name)
        existing_foreign_keys = cls.get_existing_foreign_keys(cursor, table_name)

        # Add new columns and modify existing ones
        for column, column_props in schema.items():
            column_type = column_props["type"]
            is_required = column_props.get("required", False)
            is_unique = column_props.get("unique", False)
            foreign_key = column_props.get("foreign_key")
            primary_key = column_props.get("primary_key", False)
            default = column_props.get("default", None)
            on_delete = column_props.get("on_delete", "CASCADE")  # 🔥 Default CASCADE
            on_update = column_props.get("on_update", "CASCADE")  # 🔥 Default CASCADE

            if column not in existing_columns:
                alter_query = (
                    f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type};"
                )
                cursor.execute(alter_query)
                cls.log_change(
                    "ADD COLUMN", f"Column '{column}' added to '{table_name}'"
                )

                if is_required:
                    cursor.execute(
                        f"ALTER TABLE {table_name} ALTER COLUMN {column} SET NOT NULL;"
                    )
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' marked as NOT NULL",
                    )

                if is_unique:
                    cursor.execute(
                        f"ALTER TABLE {table_name} ADD CONSTRAINT {column}_unique UNIQUE ({column});"
                    )
                    cls.log_change(
                        "ADD CONSTRAINT",
                        f"Column '{column}' in '{table_name}' is now UNIQUE",
                    )

                if foreign_key:
                    cls.add_foreign_key(
                        cursor, table_name, column, foreign_key, on_delete, on_update
                    )
                elif column in existing_foreign_keys:
                    cls.remove_foreign_key(cursor, table_name, column)

                if default:
                    cursor.execute(
                        f"ALTER TABLE {table_name} ALTER COLUMN {column} SET DEFAULT '{default}'::{column_type};"
                    )
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' set default to '{default}'::{column_type}",
                    )

                if primary_key:
                    cursor.execute(
                        f"ALTER TABLE {table_name} ADD PRIMARY KEY ({column});"
                    )
                    cls.log_change(
                        "ADD PRIMARY KEY",
                        f"Primary key '{column}' added to '{table_name}'",
                    )

                if column_props.get("track_changes", False):
                    cls.enable_data_tracking(cursor, table_name, schema)
            else:
                if existing_columns[column].get("type") != column_type:
                    alter_query = f"ALTER TABLE {table_name} ALTER COLUMN {column} TYPE {column_type} USING {column}::{column_type};"
                    cursor.execute(alter_query)
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' is now of type {column_type}",
                    )

                if is_required and not existing_columns[column].get("required"):
                    cursor.execute(
                        f"ALTER TABLE {table_name} ALTER COLUMN {column} SET NOT NULL;"
                    )
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' marked as NOT NULL",
                    )

                if not is_required and existing_columns[column].get("required"):
                    cursor.execute(
                        f"ALTER TABLE {table_name} ALTER COLUMN {column} DROP NOT NULL;"
                    )
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' marked as NULLABLE",
                    )

                if is_unique and not existing_columns[column].get("unique"):
                    # Drop if exists and add again
                    cursor.execute(
                        f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {column}_unique;"
                    )
                    # Add unique constraint
                    cursor.execute(
                        f"ALTER TABLE {table_name} ADD CONSTRAINT {column}_unique UNIQUE ({column});"
                    )
                    cls.log_change(
                        "ADD CONSTRAINT",
                        f"Column '{column}' in '{table_name}' is now UNIQUE",
                    )

                if not is_unique and existing_columns[column].get("unique"):
                    cursor.execute(
                        f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {column}_unique;"
                    )
                    cls.log_change(
                        "DROP CONSTRAINT",
                        f"Column '{column}' in '{table_name}' is no longer UNIQUE",
                    )

                if foreign_key and existing_foreign_keys.get(column) != foreign_key:
                    cls.remove_foreign_key(cursor, table_name, column)
                    cls.add_foreign_key(
                        cursor, table_name, column, foreign_key, on_delete, on_update
                    )
                    cls.log_change(
                        "ALTER FOREIGN KEY",
                        f"Foreign key '{column}' -> '{foreign_key}.id' in '{table_name}'",
                    )

                if not foreign_key and existing_foreign_keys.get(column):
                    cls.remove_foreign_key(cursor, table_name, column)
                    cls.log_change(
                        "REMOVE FOREIGN KEY",
                        f"FK '{column}' removed from '{table_name}'",
                    )

                if default and existing_columns[column].get("default") != default:
                    cursor.execute(
                        f"ALTER TABLE {table_name} ALTER COLUMN {column} SET DEFAULT '{default}'::{ existing_columns[column].get('type')};"
                    )
                    cls.log_change(
                        "ALTER COLUMN",
                        f"Column '{column}' in '{table_name}' set to default '{default}'",
                    )

        # Disable data tracking if a field no longer has track_changes
        cls.disable_removed_tracking_fields(cursor, table_name, schema)

        # Remove obsolete columns
        cls.remove_obsolete_columns(cursor, table_name, existing_columns, schema)

    @classmethod
    def enable_data_tracking(cls, cursor, table_name: str, schema: dict):
        """Enable data change tracking for fields with track_changes=True."""
        tracking_fields = [
            col for col, props in schema.items() if props.get("track_changes")
        ]

        if tracking_fields:
            trigger_name = f"{table_name}_track_changes"
            function_name = f"{table_name}_track_function"

            # Create tracking function if it does not exist
            cursor.execute(
                f"""
                CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, new_value, change_type)
                        SELECT TG_TABLE_NAME, col, NEW.col::TEXT, 'INSERT'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col);
                        RETURN NEW;
                    ELSIF TG_OP = 'UPDATE' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, old_value, new_value, change_type)
                        SELECT TG_TABLE_NAME, col, OLD.col::TEXT, NEW.col::TEXT, 'UPDATE'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col)
                        WHERE OLD.col IS DISTINCT FROM NEW.col;
                        RETURN NEW;
                    ELSIF TG_OP = 'DELETE' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, old_value, change_type)
                        SELECT TG_TABLE_NAME, col, OLD.col::TEXT, 'DELETE'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col);
                        RETURN OLD;
                    END IF;
                END;
                $$ LANGUAGE plpgsql;
            """
            )

            # Create trigger to capture changes
            cursor.execute(
                f"""
                DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
                CREATE TRIGGER {trigger_name}
                AFTER INSERT OR UPDATE OR DELETE ON {table_name}
                FOR EACH ROW EXECUTE FUNCTION {function_name}();
            """
            )

            cls.log_change(
                "ENABLE DATA TRACKING",
                f"Data change tracking enabled in '{table_name}' for {tracking_fields}",
            )

    @classmethod
    def enable_unaccent_extension(cls, cursor):
        """Enable the 'unaccent' extension in the database."""
        print("🚀 Enabling 'unaccent' extension...if not enabled")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
        cls.log_change("ENABLE EXTENSION", "Extension 'unaccent' enabled")

    @classmethod
    def disable_removed_tracking_fields(cls, cursor, table_name: str, schema: dict):
        """Disable data tracking on removed or track_changes=False columns."""
        tracking_fields = [
            col for col, props in schema.items() if props.get("track_changes")
        ]

        trigger_name = f"{table_name}_track_changes"
        function_name = f"{table_name}_track_function"

        if tracking_fields:
            # Update the tracking function with the new fields
            cursor.execute(
                f"""
                CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, new_value, change_type)
                        SELECT TG_TABLE_NAME, col, NEW.col::TEXT, 'INSERT'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col);
                        RETURN NEW;
                    ELSIF TG_OP = 'UPDATE' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, old_value, new_value, change_type)
                        SELECT TG_TABLE_NAME, col, OLD.col::TEXT, NEW.col::TEXT, 'UPDATE'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col)
                        WHERE OLD.col IS DISTINCT FROM NEW.col;
                        RETURN NEW;
                    ELSIF TG_OP = 'DELETE' THEN
                        INSERT INTO migration_logs_data (table_name, column_name, old_value, change_type)
                        SELECT TG_TABLE_NAME, col, OLD.col::TEXT, 'DELETE'
                        FROM (SELECT UNNEST(ARRAY[{', '.join([f"'{col}'" for col in tracking_fields])}])) AS t(col);
                        RETURN OLD;
                    END IF;
                END;
                $$ LANGUAGE plpgsql;
            """
            )

        else:
            # No more fields with track_changes=True, remove trigger and function
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};")
            cursor.execute(f"DROP FUNCTION IF EXISTS {function_name} CASCADE;")
            cls.log_change(
                "DISABLE DATA TRACKING", f"Data tracking removed in '{table_name}'"
            )


if __name__ == "__main__":
    Migration.run()
