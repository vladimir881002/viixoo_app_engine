from viixoo_core.routes.base_controller import BaseController
from ..services.example_service import ExampleService

service = ExampleService()


def register_routes(controller: BaseController):
    """Registra las rutas específicas del módulo 'example'."""
    controller.add_route("/example", service.get_all_examples, methods=["GET"])
    controller.add_route("/example/{id}", service.get_example, methods=["GET"])
    controller.add_route("/example", service.create_examples, methods=["POST"])

register_routes = register_routes
