import uuid

"""
  Product base class
  
  Attributes:
    id: str - The product's unique identifier
    name: str - The product's name
    
  Methods:
    __str__(self) -> str: Returns the product's string representation
"""
class Product:
    def __init__(self, name: str):
        self.id = "PR-" + str(uuid.uuid4())[:8]
        self.name = name
    
    # Return the product's string representation
    def __str__(self) -> str:
        return f"Product(id={self.id}, name={self.name})"
    