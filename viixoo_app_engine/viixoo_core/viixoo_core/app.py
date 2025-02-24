import importlib
import pkgutil
from fastapi import FastAPI, APIRouter, Request
from ..controllers import BaseController
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
import viixoo_apps  # Importar el paquete base de módulos

API_PREFIX = "/v1"

app = FastAPI(title="An app powered by Viixoo App Engine. 🚀")

# Cargar dinámicamente todos los módulos dentro de viixoo_apps
def load_modules():
    for _, module_name, _ in pkgutil.iter_modules(viixoo_apps.__path__):
        module_full_name = f"viixoo_apps.{module_name}.routes"
        try:
            module = importlib.import_module(module_full_name)  # Importar el módulo routes
            if hasattr(module, "register_routes"):
                router = APIRouter()
                controller = BaseController(router)
                module.register_routes(controller)  # Registrar rutas
                app.include_router(router)
                print(f"✅ Módulo cargado: {module_full_name}")
            else:
                print(f"⚠️ {module_full_name} no tiene register_routes, ignorando...")
        except ModuleNotFoundError:
            print(f"⚠️ {module_full_name} no encontrado, ignorando...")

# Llamar a la función para cargar los módulos dinámicamente
load_modules()

@app.get(f"{API_PREFIX}/healthcheck")
async def healthcheck():
    return "OK"

@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(f"{API_PREFIX}/docs")

@app.get("/v1", include_in_schema=False)
async def v1():
    return RedirectResponse(f"{API_PREFIX}/docs")

@app.get(f"{API_PREFIX}/docs", include_in_schema=False)
async def swagger_ui_html(request: Request) -> HTMLResponse:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("viixoo_core.app:app", host="0.0.0.0", port=8000)
