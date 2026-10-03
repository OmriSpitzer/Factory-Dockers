import uuid

from workers.base import BaseWorker
from workers.objects.product import Product

class Assembler(BaseWorker):
    def __init__(self):
        self.id = "ASSEMBLER-" + str(uuid.uuid4())[:8]
        super().__init__(self.id, 10)

    def returned_product(self, input: str) -> Product:
        return Product(input)

if __name__ == "__main__":
    from workers.lib.env_funcs import run_worker
    run_worker(Assembler, "Run an assembler worker")
