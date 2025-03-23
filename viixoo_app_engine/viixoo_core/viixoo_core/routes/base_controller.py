"""Base controller class for all controllers in the application."""

from fastapi import APIRouter
from typing import List, Callable


class BaseController:
    """Base controller class for all controllers in the application."""

    def __init__(self, router: APIRouter):
        """Initialize a BaseController instance."""
        self.router = router

    def add_route(self, path: str, func: Callable, methods: List[str] = ["GET"]):
        """Register a route dynamically within the controller.

        :param path: route path
        :param func: route function
        :param methods: HTTP methods
        """
        self.router.add_api_route(path, func, methods=methods)

    def success_response(self, data: dict):
        """Return a response with a success message and data.

        :param data: data to be returned
        """
        return {"status": "success", "data": data}

    def error_response(self, message: str, status_code: int = 400):
        """Return a response with an error message.

        :param message: error message
        :param status_code: HTTP status code
        """
        return {"status": "error", "message": message, "status_code": status_code}
