from workers.base import BaseWorker
from workers.objects.product import Product
from workers.objects.package import Package
import uuid

class Packager(BaseWorker):
    def __init__(self):
        self.id = "PACKAGER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 5)
    
    def returned_product(self, input: Product) -> Package:
        return Package(input)

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Packager, "Run a packager worker")