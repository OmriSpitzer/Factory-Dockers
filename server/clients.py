import random
import threading
import uuid

"""
  Client class

  Attributes:
    client_id: str - The client's unique identifier
    person_name: str - The client's name
    timeout: int - The client's timeout
    image: str - The client's image
    _stopped: threading.Event - The event to stop the client

  Methods:
    run(self) -> None: Run the client
    stop(self) -> None: Stop the client
    snapshot(self) -> dict: Get the client's snapshot
"""

# Default first names
FIRST_NAMES = (
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen",
)

# Default last names
LAST_NAMES = (
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin",
)

class Client(threading.Thread):
    def __init__(self, name: str,timeout:tuple[int,int] = (5, 10)) -> None:
        super().__init__(name=name, daemon=True)
        self.client_id = str(uuid.uuid4())
        self.name = name
        self.timeout = random.randint(timeout[0], timeout[1])
        self.image = "/client.png"
        self._stopped = threading.Event()

    # Run the client
    def run(self) -> None:
        self._stopped.wait()

    # Stop the client
    def stop(self) -> None:
        self._stopped.set()
    
    # Get the client's dictionary
    def snapshot(self) -> dict:
        return {
            "id": self.client_id,
            "name": self.name,
            "timeout": self.timeout,
            "image": self.image,
        }
    
    # Get the client's string representation
    def __str__(self) -> str:
        return f"Client(id={self.client_id}, name={self.name}, timeout={self.timeout})"

class ClientPool:
    CLIENT_TIMEOUT = (6, 12)

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: list[Client] = []

    # Add a client to the pool
    def add(self) -> dict:
        with self._lock:
            name = self._random_name({client.name for client in self._clients})
            client = Client(name, timeout=self.CLIENT_TIMEOUT)
            self._clients.append(client)
        client.start()
        return client.snapshot()

    # Remove the last client from the pool
    def remove_last(self) -> dict | None:
        with self._lock:
            if not self._clients:
                return None
            client = self._clients.pop()
        
        # Stop the client
        client.stop()
        client.join(timeout=1)
        return client.snapshot()

    # Get all clients
    def all(self) -> list[dict]:
        with self._lock:
            return [client.snapshot() for client in self._clients]

    # Generate a random name
    def _random_name(self, used: set[str]) -> str:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        for _ in range(12):
            if name not in used:
                return name
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        return name
