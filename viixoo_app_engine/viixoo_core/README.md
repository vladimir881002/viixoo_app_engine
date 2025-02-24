# viixoo_app_engine
Microframework used by Viixoo to develop microservices and distribute applications.

📌 Installation and Execution

1. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # Or `env\Scripts\activate` on Windows

2-Install the dependencies:
pip install -r requirements.txt or pip install -r requirements-dev.txt

3-Run the application:
python app.py # This might be outdated, see below for using uvicorn

uvicorn viixoo_core.app:app --reload

or execute directly: viixoo_core_run

if the package is install just do a viixoo_core_run

📌 Explanation of the Structure:

viixoo_core/: Contains the core logic of the framework, such as the entry point (app.py), base controllers, services, models, and the QWeb renderer.
viixoo_apps/: This is where the backend modules reside, each with its own controller and service.
viixoo_apps_frontend/: Modular structure similar to the backend, but with OWL components, QWeb templates, and frontend services.
templates/: QWeb templates shared by the application.
static/: Static files such as HTML, JavaScript, and CSS styles.
dist/: Distribution folder for the framework (useful for packaging and distribution).
Root files (setup.py, requirements.txt, package.json, README.md): Environment configuration and dependencies.

viixoo_app_engine/
│── viixoo_core/                 # Framework Core
│   │── __init__.py
│   │── app.py                    # FastAPI application entry point
│   │── controllers.py             # Base controller for inheritance
│   │── services.py                # Base services
│   │── models.py                  # Data models using Pydantic
│   │── qweb_renderer.py           # QWeb template renderer
│
│── viixoo_apps/                  # Backend Modules
│   ├── example/
│   │   │── __init__.py
│   │   │── controllers.py         # Module-specific controllers
│   │   │── services.py            # Module business logic
│
│── viixoo_apps_frontend/         # Frontend Modules (OWL + QWeb)
│   ├── example/
│   │   │── __init__.py
│   │   │── components/            # OWL Components
│   │   │   ├── ExampleComponent.js
│   │   │── templates/             # QWeb Templates
│   │   │   ├── example_template.xml
│   │   │── routes.py              # Frontend route definitions
│   │   │── services.py            # Frontend services
│
│── templates/                    # General Templates
│   │── home.xml
│
│── static/                       # Static files (CSS, JS, images)
│   │── index.html
│   │── main.js
│
│── dist/                         # Framework Distribution
│   │── viixoo_core-0.1.0.tar.gz
│
│── setup.py                      # Package installation configuration
│── requirements.txt               # Project dependencies
│── package.json                   # Frontend dependencies
│── README.md                      # Project documentation


📌 Explanation of Dependencies:

fastapi: Fast, modern web framework for the backend.
uvicorn: Recommended ASGI server for running FastAPI applications. (Start the application with: uvicorn viixoo_core.app:app --reload)
pydantic: Data validation and data model management.
psycopg[binary]: Driver for connecting to PostgreSQL.
Jinja2: Used in QWeb, as QWeb in Odoo is based on Jinja.

📌 Explanation of setup.py:

find_packages(): Automatically detects packages within the project.
install_requires: List of required dependencies (same as in requirements.txt).
entry_points: Allows running the application from the command line (viixoo_app_engine).
include_package_data=True: Includes additional files like templates and static assets.
classifiers: Metadata about the project, useful for PyPI.

🚀 Testing with Multiple Modules
If we have these modules:
viixoo_apps/
│── example/
│   ├── __init__.py
│   ├── routes.py
│── users/
│   ├── __init__.py
│   ├── routes.py
│── products/
│   ├── __init__.py
│   ├── routes.py  ❌ (Optional, may not exist)

The framework will automatically load modules that have a routes.py file.

📄 Example of routes.py in viixoo_apps/users/routes.py:

async def get_users():
    return [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]

async def get_user_by_id(id: int):
    return {"id": id, "name": f"User {id}"} if id == 1 else {"error": "Not found"}

def register_routes(controller):
    """Registers the specific routes for the 'users' module."""
    controller.add_route("/users", get_users, methods=["GET"])
    controller.add_route("/users/{id}", get_user_by_id, methods=["GET"])

🔥 How it Works Now

When you start FastAPI (using uvicorn viixoo_core.app:app --reload), the framework:

Detects example/routes.py automatically.
Calls register_routes(), which adds the routes to the BaseController.
FastAPI registers these routes without modifying app.py.

2. Test in the browser or with curl:

Get all examples:
    GET http://127.0.0.1:8000/example

    [
        {"id": 1, "name": "Example 1"},
        {"id": 2, "name": "Example 2"}
    ]

Get an example by ID:
    GET http://127.0.0.1:8000/example/1
    {"id": 1, "name": "Example 1"}



