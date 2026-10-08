import threading
from dataclasses import asdict, replace
from typing import Any
from objects.record import Entry, Record

"""
  Server connection class

  Methods:
    set(self, worker_id: str, sock, message: dict) -> dict: Set the connection
    upsert(self, message: dict) -> dict: Upsert the connection
    update(self, worker_id: str, message: dict) -> dict | None: Update the connection
    remove(self, worker_id: str, sock=None) -> None: Remove the connection
    get(self, worker_id: str) -> dict | None: Get the connection
    all(self) -> list[dict]: Get all connections
"""

class Connection:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_id: dict[str, Entry] = {}

    # Set the connection
    def set(self, worker_id: str, sock, message: dict) -> dict:
        with self._lock:
            record = self._record(worker_id, message)
            self._by_id[worker_id] = Entry(connection=sock, record=record)
            return asdict(record)

    # Upsert the connection
    def upsert(self, message: dict) -> dict:
        with self._lock:
            # Get metadata
            worker_id = str(message["id"])
            current = self._by_id.get(worker_id)
            sock = current.connection if current else None

            # Update the connection
            record = self._record(worker_id, message)
            self._by_id[worker_id] = Entry(connection=sock, record=record)
            return asdict(record)

    # Update the connection
    def update(self, worker_id: str, message: dict) -> dict | None:
        with self._lock:
            current = self._by_id.get(worker_id)
            if current is None:
                return None

            # Update the connection
            record = replace(current.record, **self._changes(current.record, message))
            current.record = record
            return asdict(record)

    # Remove the connection
    def remove(self, worker_id: str, sock=None) -> None:
        with self._lock:
            current = self._by_id.get(worker_id)
            if current is None:
                return
            if sock is not None and current.connection is not sock:
                return

            # Remove the connection
            del self._by_id[worker_id]

    # Get by id the connection
    def get(self, worker_id: str) -> dict | None:
        with self._lock:
            current = self._by_id.get(worker_id)
            return asdict(current.record) if current else None

    # Get all connections
    def all(self) -> list[dict]:
        with self._lock:
            return [asdict(entry.record) for entry in self._by_id.values()]

    # Record the connection
    def _record(self, worker_id: str, message: dict) -> Record:
        worker = message.get("worker")
        if isinstance(worker, dict):
            worker = dict(worker)
        return Record(id=worker_id, worker=worker, result=message.get("result"))

    # Get the changes
    def _changes(self, record: Record, message: dict) -> dict:
        changes: dict[str, Any] = {}
        if "worker" in message:
            worker = message["worker"]
            changes["worker"] = dict(worker) if isinstance(worker, dict) else worker
        if "result" in message:
            changes["result"] = message["result"]
        return changes


# The connections
connections = Connection()
