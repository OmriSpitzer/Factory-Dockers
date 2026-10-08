from workers.objects.product import Product

"""
  Tested product object class
  
  Attributes:
    id: str - The tested product's unique identifier
    name: str - The tested product's name
    
  Methods:
    __str__(self) -> str: Returns the tested product's string representation
"""
class TestedProduct(Product):
    def __init__(self, product: Product):
        super().__init__(product.name)

    # Return the tested product's string representation
    def __str__(self) -> str:
        return f"TestedProduct(id={self.id}, name={self.name})"