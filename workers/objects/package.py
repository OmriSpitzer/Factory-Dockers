from workers.objects.product import Product

"""
  Package object class
  
  Attributes:
    id: str - The package's unique identifier
    name: str - The package's name
    
  Methods:
    __str__(self) -> str: Returns the package's string representation
"""
class Package(Product):
    def __init__(self, product: Product):
        super().__init__(product.name)

    # Return the package's string representation
    def __str__(self) -> str:
        return f"Package(id={self.id}, name={self.name})"