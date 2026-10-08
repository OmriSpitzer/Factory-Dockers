from workers.base import BaseWorker
from workers.objects.product import Product
from workers.objects.package import Package
import uuid

"""
  Packager worker class

  Attributes:
    id: str - The worker's unique identifier

  Methods:
    returned_product(self, input: Product) -> Package: Returns the packaged product
    to_dict(self) -> dict: Returns the worker's metadata as a dictionary
"""
class Packager(BaseWorker):
    def __init__(self):
        self.id = "PACKAGER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 5)
    
    # Return the packaged product
    def returned_product(self, input: Product) -> Package:
        return Package(input)

    # Convert the worker to a dictionary
    def to_dict(self) -> dict:
        return super().to_dict()

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Packager, "Run a packager worker")