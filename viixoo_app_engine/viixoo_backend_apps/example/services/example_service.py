"""Show how to use the base service and viixoo core package."""

from ..models.example_model import ExampleModel
from viixoo_core.services.base_service import BaseService


class ExampleService(BaseService):
    """Example service."""

    def __init__(self):
        """Simulate an in memorie database."""
        super().__init__("example")

        self.examples = [
            ExampleModel(id=1, name="Ejemplo 1", extra_field=1),
            ExampleModel(id=2, name="Ejemplo 2", extra_field=2),
        ]

    def get_all_examples(self):
        """Return all examples."""
        return [example.model_dump() for example in self.examples]

    def get_example(self, id: int):
        """Return example by id."""
        for example in self.examples:
            if example.id == id:
                return example.model_dump()
        return {"error": "Not found"}

    def create_examples(self):
        """Create examples in database."""
        for example in self.examples:
            example.create(rows=[example.model_dump()])

            print(example.model_dump())
