from workers.base import BaseWorker
from workers.objects.product import Product
from workers.objects.tested_product import TestedProduct
import uuid

"""
  Tester worker class

  Attributes:
    id: str - The worker's unique identifier

  Methods:
    returned_product(self, input: Product) -> TestedProduct: Returns the tested product
    to_dict(self) -> dict: Returns the worker's metadata as a dictionary
"""
class Tester(BaseWorker):
    def __init__(self):
        self.id = "TESTER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 15)
    
    # Return the tested product
    def returned_product(self, input: Product) -> TestedProduct:
        return TestedProduct(input)

    # Convert the worker to a dictionary
    def to_dict(self) -> dict:
        return super().to_dict()

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Tester, "Run a tester worker")