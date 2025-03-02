# Viixoo App Engine

A microframework used by Viixoo to develop microservices and distribute applications.

## 🚀 Installation and Execution

1.  **Create a virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate  # Or `env\Scripts\activate` on Windows
    ```

2.  **Install the dependencies:**

    ```bash
    cd viixoo_app_engine/viixoo_core
    pip install -r requirements-dev.txt # or
    pip install -e .[dev] # install project in editable mode with dev dependencies
    pip install -r requirements.txt # install project with dependencies (production environment)
    ```

3.  **Run the application:**

    ```bash
    cd viixoo_app_engine/viixoo_core
    uvicorn viixoo_core.app:app --reload
    ```

    Alternatively, if the package is installed, you can use the shortcut:

    ```bash
    viixoo_run
    ```

## 🧰 Commands

Here's a list of useful commands for working with the Viixoo App Engine:

### Managing the Virtual Environment

*   **Create a virtual environment:**

    ```bash
    python -m venv env
    ```

    *   **`python -m venv env`**: Creates a virtual environment named `env` in the current directory.
*   **Activate the virtual environment (Linux/macOS):**

    ```bash
    source env/bin/activate
    ```

    *   **`source env/bin/activate`**: Activates the virtual environment.
*   **Activate the virtual environment (Windows):**

    ```bash
    env\Scripts\activate
    ```

    *   **`env\Scripts\activate`**: Activates the virtual environment.

### Running the Application

*   **Run the application with `uvicorn`:**

    ```bash
    uvicorn viixoo_core.app:app --reload
    ```

    *   **`uvicorn`**: The command to run the Uvicorn server.
    *   **`viixoo_core.app:app`**: The module (`viixoo_core.app`) and the FastAPI instance (`app`) to run.
    *   **`--reload`**: Enables automatic reloading when code changes are detected.

*   **Run the application using the shortcut:**

    ```bash
    viixoo_run
    ```

    *   **`viixoo_run`**: If the package is installed in your environment, you can use this shortcut to run the application.

### Managing Migrations

* **Run all migrations**
    ```bash
    viixoo_migrate
    ```

* **Convert Odoo models**
    ```bash
    viixoo_convert <path_to_python_odoo_model> <path_to_output>
    ```
    This command facilitates the conversion of Odoo models to valid Viixoo_core models. It provides a basic conversion, enabling faster migration when reusing Odoo models is a viable option.

### 📂 Project Structure

This project is organized into several key directories:
```
viixoo_app_engine/
├── viixoo_core/                 # Framework Core
│   ├── __init__.py
│   ├── app.py                    # FastAPI application entry point
│   ├── controllers.py             # Base controller for inheritance
│   ├── services.py                # Base services
│   ├── models/                  # Data models using Pydantic
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── postgres.py
│   ├── config.py                  # Configuration management
│   ├── import_utils.py            # Import utility
│   ├── migrations.py              # Manages migrations
│   ├── domain.py                  # Translates domains to SQL
│   └── ...
├── viixoo_backend_apps/                  # Backend Modules
│   └── example/
│       ├── __init__.py
│       ├── controllers.py         # Module-specific controllers
│       ├── services.py            # Module business logic
│       ├── models.py              # Module models
│       └── routes.py
├── viixoo_frontend_apps/         # Frontend Modules (OWL + QWeb) TBD
│   └── example/
│       ├── __init__.py
│       ├── components/            # OWL Components
│       │   └── ExampleComponent.js
│       ├── templates/             # QWeb Templates
│       │   └── example_template.xml
│       ├── routes.py              # Frontend route definitions
│       └── services.py            # Frontend services
├── setup.py                      # Package installation configuration
├── requirements-dev.txt          # Development dependencies
└── README.md                     # Project documentation
```

### Core Components (`viixoo_core/`)

*   **`__init__.py`:** Makes the `viixoo_core` directory a Python package.
*   **`app.py`:** The main entry point for the FastAPI application. It handles route loading and configuration.
*   **`routes/base_controller.py`:** Contains the `BaseController` class, which provides a foundation for creating specific controllers.
*   **`services/base_services.py`:** Defines the `BaseService` class, the foundation for creating services.
*   **`models/`:**  Directory with model classes:
    *   **`__init__.py`**: makes models a python package
    *   **`base.py`**: Defines the `BaseDBModel` class, the base for all database models.
    *   **`postgres.py`**: Defines the `PostgresModel` class, the base for all postgres models.
    *   **`domain.py`**: Translates a domain in to a SQL query.
* **`config.py`**: load config from env vars or `.conf` file, the config file have to be located in app root folder
* **`import_utils.py`**: load modules, and get all modules names. Helper functions to dynamic load modules.
* **`migrations.py`**: Handles database migrations.

### Backend Modules (`viixoo_backend_apps/`)

*   **`example/`:** An example of a backend module.
    *   **`__init__.py`:** Makes the `example` directory a Python package.
    *   **`models/`:**  Directory with model classes:
        *   **`__init__.py`**: makes models a python package
        *   **`example_model.py`**: A model example for the `example` module.
    *   **`routes.py`:** Defines the API routes for this module.
        *   **`__init__.py`**: makes models a python package
        *   **`routes.py`**: A route example for the `example` module.
    *   **`services/`:**  Directory with controller classes:
        *   **`__init__.py`**: makes controllers a python package
        *   **`example_service.py`**: A controller example for the `example` module.

### General Files

*   **`pyproject.toml`:** Used for packaging and installing the `viixoo_core` framework.
*   **`requirements-dev.txt`:** Lists the development dependencies of the project.
*   **`requirements.txt`:** Lists the dependencies of the project.
*   **`README.md`:** This documentation file.

## 🗂️ Explanation of Dependencies:

*   **`fastapi`:** A fast and modern web framework for building APIs (the backend).
*   **`uvicorn`:** A high-performance ASGI server, recommended for running FastAPI applications. Use: `uvicorn viixoo_core.app:app --reload`
*   **`pydantic`:** A library for data validation and data model management.
*   **`psycopg[binary]`:** A driver for connecting to PostgreSQL databases.
*   **`Jinja2`:** A template engine used as the basis for QWeb templates.
*   **`pytest`**: A test framework.
*   **`pytest-cov`**: coverage plugin for pytest

## 🚀 Testing with Multiple Modules

If you have the following modules:


The framework automatically loads modules that have a `routes.py` file.

## 📄 Example of `routes.py` (in `viixoo_backend_apps/users/routes.py`)

### It's recomended to have the get_users fuction an all the business logic in the service layer

```python

from viixoo_core.controllers import BaseController

async def get_users():
    return [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]

async def get_user_by_id(id: int):
    return {"id": id, "name": f"User {id}"} if id == 1 else {"error": "Not found"}

def register_routes(controller: BaseController):
    """Registers the specific routes for the 'users' module."""
    controller.add_route("/users", get_users, methods=["GET"])
    controller.add_route("/users/{id}", get_user_by_id, methods=["GET"])
```

## 🔥 How It Works
When you start FastAPI (using uvicorn viixoo_core.app:app --reload), the framework performs these steps:

Module Detection: Detects module with routes.py automatically.
Route Registration: Calls register_routes(), which adds the routes to the BaseController.
FastAPI Integration: FastAPI registers these routes, so no changes are required in app.py.
🧪 Testing the Example

### 1-Get all examples:

    GET http://127.0.0.1:8000/example

    ```
    [
        {"id": 1, "name": "Example 1"},
        {"id": 2, "name": "Example 2"}
    ]
    ```

### 2-Get an example by ID:

    GET http://127.0.0.1:8000/example/1

    ```
    {"id": 1, "name": "Example 1"}    
    ```

### Testing

*   **Run all tests:**

    ```bash
    pytest -v
    ```

    *   **`pytest`**: The command to run the `pytest` test runner.
    *   **`-v`**: Enables verbose output (shows more details).

* **Run the tests of a specific class:**
    ```bash
    pytest -v tests/viixoo_core/test_app.py -k TestApp
    ```
    *   **`pytest`**: The command to run the `pytest` test runner.
    *   **`-v`**: Enables verbose output (shows more details).
    *   **`tests/viixoo_core/test_app.py`**: The path to test file.
    *   **`-k TestApp`**: run only the tests of `TestApp` class.
* **Run the tests of a specific method:**
    ```bash
    pytest -v tests/viixoo_core/test_app.py -k test_load_modules_success
    ```
    *   **`pytest`**: The command to run the `pytest` test runner.
    *   **`-v`**: Enables verbose output (shows more details).
    *   **`tests/viixoo_core/test_app.py`**: The path to test file.
    *   **`-k test_load_modules_success`**: run only the test method `test_load_modules_success`.

*   **Run tests with coverage:**

    ```bash
    pytest -v --cov=viixoo_core --cov-report=term-missing --cov-report=xml:coverage.xml --junitxml=junit.xml tests/viixoo_core/
    ```

    *   **`--cov=viixoo_core`**: Specifies that you want to measure coverage for the `viixoo_core` package.
    * **`--cov-report=term-missing`**: Print missing lines in the terminal.
    * **`--cov-report=xml:coverage.xml`**: Create a XML report file.
    * **`--junitxml=junit.xml`**: Create a junit report file.
    *   **`tests/viixoo_core/`**: Specifies the folder where the test are.

* **Run tests with specific python version:**
     * The matrix of python version is defined in the `py_test.yml` file inside `github/workflows` folder.
     * For example:
        ```yaml
        strategy:
           matrix:
              python-version: ["3.9", "3.10", "3.11"]
        ```
* **Run tests with codecov**
    * This is configured in the `py_test.yml` file inside `github/workflows` folder.
    * A token from `codecov` is needed.

## 🤝 Contributing

Contributions are welcome! Please see the contributing guidelines for more details. (TBD)
