"""Base service class."""


class BaseService:
    """Base service class."""

    def __init__(self, name):
        """Initialize a BaseService instance.

        :param name: name of the service
        """
        self.name = name
