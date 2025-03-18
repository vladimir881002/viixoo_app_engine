from viixoo_core.routes.base_controller import BaseController
from ..services.mrp_service import MrpService

service = MrpService()

def register_routes(controller: BaseController):
    controller.add_route("/login/access-token", service.authenticate_user, methods=["POST"])
    controller.add_route("/users/me", service.get_user, methods=["GET"])
    controller.add_route("/users/me/password", service.reset_password, methods=["PATCH"])
    controller.add_route("/production-orders", service.get_production_orders, methods=["GET"])
    controller.add_route("/work-orders", service.get_workorders, methods=["GET"])
    controller.add_route("/reasons-loss", service.get_reasons_loss, methods=["GET"])
    controller.add_route("/workorder/start", service.start_workorder, methods=["PATCH"])
    controller.add_route("/workorder/block", service.block_workorder, methods=["PATCH"])
    controller.add_route("/workorder/unblock", service.unblock_workorder, methods=["PATCH"])
    controller.add_route("/workorder/finish", service.finish_workorder, methods=["PATCH"])
    controller.add_route("/workorder/pause", service.pause_workorder, methods=["PATCH"])

register_routes = register_routes
