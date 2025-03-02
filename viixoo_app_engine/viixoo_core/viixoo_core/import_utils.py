import os
import sys
import pkgutil
import importlib
from typing import List, Any

APPS_PATH_DEFINED: str = os.environ.get("APPS_PATH", "")
APPS_PATH: str = os.path.join(os.path.dirname(__file__), "../../viixoo_backend_apps")

if APPS_PATH_DEFINED:
    APPS_PATH = APPS_PATH_DEFINED

print(f"📂 APPS_PATH: {APPS_PATH}")

class ImportUtils:
    ### Finds all the modules in the APPS_PATH ###

    @classmethod
    def get_modules(cls) -> List[str]:
        """Gets the application modules."""
        print("🔍 Searching for application modules...")
        modules = []
        print(f"📂 Searching in path: {APPS_PATH}")
        for _, module_name, _ in pkgutil.iter_modules([APPS_PATH]):
            modules.append(module_name)
            print(f"📦 Module found: {module_name}")
        return modules
    
    @classmethod
    def import_module(cls, module_full_path: str, module_name: str) -> Any:
        """Imports a module given its name."""
        print(f"📦 Importing module: {module_full_path}")
        try:
            module = importlib.import_module(module_full_path)
            print(f"📦 Module imported: {module_name}")
            return module
        except ImportError as e:
            print(f"❌ Error importing module '{module_name}': {e}")
            return None
    
    @classmethod
    def import_module_from_path(cls, module_path: str) -> dict[str, Any]:
        """Imports a module from the given path. Function to dynamically import a module given its full module_path

        Args:
            module_path: The path to the module directory.

        Returns:
            A dictionary where keys are modules package names and values are the top-level
            module objects of the packages. Returns an empty dictionary if no modules
            are found or an error occurred.
        """
        modules = {}
        try:
            for item in os.listdir(module_path):
                item_path = os.path.join(module_path, item)
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):  # Check for package
                    package_name = item  # The directory name is the package name
                    init_path = os.path.join(item_path, "__init__.py")

                    spec = importlib.util.spec_from_file_location(package_name, init_path) # Important: use __init__.py
                    if spec is None:
                        continue

                    package = importlib.util.module_from_spec(spec)
                    if package is None:
                        continue

                    sys.modules[package_name] = package  # Add to sys.modules
                    spec.loader.exec_module(package)

                    modules[package_name] = package

        except FileNotFoundError:
            print(f"🚨 Module directory '{module_path}' not found.")
        except Exception as e:
            print(f"❌ Error loading plugins: {e}")

        return modules
