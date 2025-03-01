from fastapi import APIRouter
from typing import List, Callable

class BaseController:
    def __init__(self, router: APIRouter):
        self.router = router

    def add_route(self, path: str, func: Callable, methods: List[str] = ["GET"]):
        """Permite registrar rutas dinámicamente en el controlador."""
        self.router.add_api_route(path, func, methods=methods)

    def success_response(self, data: dict):
        return {"status": "success", "data": data}

    def error_response(self, message: str, status_code: int = 400):
        return {"status": "error", "message": message, "status_code": status_code}
