from viixoo_apps.example.models.example_model import ExampleModel
from viixoo_app_engine.viixoo_core.viixoo_core.services import BaseService


class ExampleService(BaseService):
    def __init__(self):        
        """Simula una base de datos con datos en memoria"""
        
        super().__init__("example")
        
        self.examples = [
            ExampleModel(id=1, name="Ejemplo 1"),
            ExampleModel(id=2, name="Ejemplo 2"),
        ]

    def get_all_examples(self):
        return [example.model_dump() for example in self.examples]

    def get_example(self, id: int):
        for example in self.examples:
            if example.id == id:
                return example.model_dump()
        return {"error": "No encontrado"}
    
    def create_examples(self):
        for example in self.examples:
            example.create(rows=[example.model_dump()])

            print(example.model_dump())
