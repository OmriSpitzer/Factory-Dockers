from workers.objects.product import Product

class Package(Product):
    def __init__(self, product: Product):
        super().__init__(product.name)

    def __str__(self) -> str:
        return f"Package(id={self.id}, name={self.name})"