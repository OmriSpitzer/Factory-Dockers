import random
import threading
import uuid

FIRST_NAMES = (
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen",
)
LAST_NAMES = (
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin",
)


class Client(threading.Thread):
    def __init__(self, used_names: set[str]) -> None:
        self.client_id = str(uuid.uuid4())
        self.person_name = _random_name(used_names)
        self.timeout = random.randint(5, 10)
        self.image = "/client.png"
        super().__init__(name=self.person_name, daemon=True)
        self._stopped = threading.Event()

    def run(self) -> None:
        self._stopped.wait()

    def stop(self) -> None:
        self._stopped.set()

    def snapshot(self) -> dict:
        return {
            "id": self.client_id,
            "name": self.person_name,
            "timeout": self.timeout,
            "image": self.image,
        }


class ClientThreads:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._threads: list[Client] = []

    def add(self) -> dict:
        with self._lock:
            used = {thread.person_name for thread in self._threads}
            client = Client(used)
            self._threads.append(client)
        client.start()
        return client.snapshot()

    def remove_last(self) -> dict | None:
        with self._lock:
            if not self._threads:
                return None
            client = self._threads.pop()
        client.stop()
        client.join(timeout=1)
        return client.snapshot()

    def all(self) -> list[dict]:
        with self._lock:
            return [thread.snapshot() for thread in self._threads]


def _random_name(used: set[str]) -> str:
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    for _ in range(12):
        if name not in used:
            return name
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    return name


threads = ClientThreads()
