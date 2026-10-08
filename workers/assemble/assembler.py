import uuid

from workers.base import BaseWorker
from workers.objects.product import Product

"""
  Assembler worker class
  
  Attributes:
    id: str - The worker's unique identifier
    
  Methods:
    returned_product(self, input: str) -> Product: Returns the assembled product
    to_dict(self) -> dict: Returns the worker's metadata as a dictionary
"""
class Assembler(BaseWorker):
    def __init__(self):
        self.id = "ASSEMBLER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 10)

    # Return the assembled product
    def returned_product(self, input: str) -> Product:
        return Product(input)

    # Convert the worker to a dictionary
    def to_dict(self) -> dict:
        return super().to_dict()

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Assembler, "Run an assembler worker")
