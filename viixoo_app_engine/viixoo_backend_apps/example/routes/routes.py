from viixoo_core.routes.base_controller import BaseController
from ..services.example_service import ExampleService

service = ExampleService()

async def get_examples():
    """Devuelve una lista de ejemplos"""
    return service.get_all_examples()

async def get_example_by_id(id: int):
    """Devuelve un ejemplo por su ID"""
    return service.get_example(id)

def register_routes(controller: BaseController):
    """Registra las rutas específicas del módulo 'example'."""
    controller.add_route("/example", get_examples, methods=["GET"])
    controller.add_route("/example/{id}", get_example_by_id, methods=["GET"])
    controller.add_route("/example", service.create_examples, methods=["POST"])

register_routes = register_routes
