from workers.base import BaseWorker
from workers.objects.package import Package
import uuid

"""
  Shipper worker class

  Attributes:
    id: str - The worker's unique identifier

  Methods:
    returned_product(self, input: Package) -> None: Returns the shipped product
    to_dict(self) -> dict: Returns the worker's metadata as a dictionary
"""
class Shipper(BaseWorker):
    def __init__(self):
        self.id = "SHIPPER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 10)
    
    # Return the shipped product
    def returned_product(self, input: Package) -> None:
        return None
    
    # Convert the worker to a dictionary
    def to_dict(self) -> dict:
        return super().to_dict()

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Shipper, "Run a shipper worker")