"""Settings module."""

import os
import configparser
from abc import ABC
from typing import Dict, Any


class BaseConfig(ABC):
    """Base class for database configuration, allowing reading from environment variables or `.conf` files."""

    @classmethod
    def from_env(cls, module) -> Dict[str, Any]:
        """Read the settings from environment variables."""
        config = {
            "db_type": os.getenv(f"{module}_DB_TYPE", False),  # Valor por defecto
            "dbname": os.getenv(f"{module}_DB_NAME", "viixoo_app_engine_test_db"),
            "user": os.getenv(f"{module}_DB_USER", "postgres"),
            "password": os.getenv(f"{module}_DB_PASSWORD", ""),
            "host": os.getenv(f"{module}_DB_HOST", "localhost"),
            "port": int(os.getenv(f"{module}_DB_PORT", 5432)),
        }
        return config

    @classmethod
    def from_file(cls, config_file: str) -> Dict[str, Any]:
        """Read the settings from a `.conf` file."""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        config = configparser.ConfigParser()
        config.read(config_file)

        return {
            "db_type": config.get("database", "db_type", fallback="postgresql"),
            "dbname": config.get("database", "dbname", fallback="viixoo_db"),
            "user": config.get("database", "user", fallback="postgres"),
            "password": config.get("database", "password", fallback=""),
            "host": config.get("database", "host", fallback="localhost"),
            "port": config.getint("database", "port", fallback=5432),
        }

    @classmethod
    def get_config(cls, base_path: str, module: str) -> Dict[str, Any]:
        """Obtiene la configuración, ya sea desde variables de entorno o archivo .conf."""
        # We prefer environment variables, if they are not there, we use the .conf file
        config = cls.from_env(module=module)
        if not config["db_type"]:
            file_path = os.path.join(base_path, f"{module}", f"{module}.conf")
            file_config = cls.from_file(file_path)
            print(f"📂 Config from file: {file_path}")
            config = {**config, **file_config}
        return config
