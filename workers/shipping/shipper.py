from workers.base import BaseWorker
from workers.objects.package import Package
import uuid

class Shipper(BaseWorker):
    def __init__(self):
        self.id = "SHIPPER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 10)
    
    def returned_product(self, input: Package) -> None:
        return None

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Shipper, "Run a shipper worker")