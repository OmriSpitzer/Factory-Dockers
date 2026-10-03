import uuid
class Product:
    def __init__(self, name: str):
        self.id = "PR-" + str(uuid.uuid4())[:8]
        self.name = name
    
    def __str__(self) -> str:
        return f"Product(id={self.id}, name={self.name})"
    