"""Main FastAPI application."""

from fastapi import FastAPI, APIRouter, Request
from viixoo_core.routes.base_controller import BaseController
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from viixoo_core.import_utils import APPS_PATH, ImportUtils

API_PREFIX = "/v1"

app = FastAPI(title="An app powered by Viixoo App Engine. 🚀")

router = APIRouter()
controller = BaseController(router)


# Cargar dinámicamente todos los módulos dentro de viixoo_backend_apps
def load_modules():
    """Load all modules in the APPS_PATH directory."""
    print(f"📂 Loading modules in path: {APPS_PATH}")
    try:
        modules = ImportUtils.import_module_from_path(APPS_PATH)
        for module in modules:
            if hasattr(modules[module], "routes"):
                _routes = modules[module].routes
                if hasattr(_routes.routes, "register_routes"):
                    _routes.routes.register_routes(controller)  # Registrar rutas
                    print(f"✅ Module loaded: {module}")
                else:
                    print(f"⚠️ {module} don't have routes, ignoring...")
    except Exception as e:
        print(f"❌ Error loading modules: {e}")
        return


# Llamar a la función para cargar los módulos dinámicamente
load_modules()

# dynamic register routers
app.include_router(router)


@app.get(f"{API_PREFIX}/healthcheck")
async def healthcheck():
    """Healthcheck endpoint."""
    return "OK"


@app.get("/", include_in_schema=False)
async def home():
    """Home endpoint.Automatically redirects to the API documentation."""
    return RedirectResponse(f"{API_PREFIX}/docs")


@app.get("/v1", include_in_schema=False)
async def v1():
    """Home endpoint. Automatically redirects to the API documentation."""
    return RedirectResponse(f"{API_PREFIX}/docs")


@app.get(f"{API_PREFIX}/docs", include_in_schema=False)
async def swagger_ui_html(request: Request) -> HTMLResponse:
    """Swagger UI HTML endpoint."""
    root_path = request.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_favicon_url="/assets/viixoo_logo.png",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


def run_app():
    """Run the FastAPI application."""
    import uvicorn

    uvicorn.run("viixoo_core.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    """Run the FastAPI application."""
    run_app()
