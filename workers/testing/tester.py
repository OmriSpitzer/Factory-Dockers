from workers.base import BaseWorker
from workers.objects.product import Product
from workers.objects.tested_product import TestedProduct
import uuid

class Tester(BaseWorker):
    def __init__(self):
        self.id = "TESTER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 15)
    
    def returned_product(self, input: Product) -> TestedProduct:
        return TestedProduct(input)

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Tester, "Run a tester worker")