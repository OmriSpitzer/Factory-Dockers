import threading


class Connection:
    """Live sockets and the JSON each worker sends, keyed by id."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_id: dict[str, dict] = {}

    def set(self, worker_id: str, sock, message: dict) -> dict:
        with self._lock:
            record = self._record(worker_id, message)
            self._by_id[worker_id] = {"connection": sock, "record": record}
            return dict(record)

    def upsert(self, message: dict) -> dict:
        with self._lock:
            worker_id = str(message["id"])
            current = self._by_id.get(worker_id)
            sock = current["connection"] if current else None
            record = self._record(worker_id, message)
            self._by_id[worker_id] = {"connection": sock, "record": record}
            return dict(record)

    def update(self, worker_id: str, message: dict) -> dict | None:
        with self._lock:
            current = self._by_id.get(worker_id)
            if current is None:
                return None
            record = current["record"]
            if "worker" in message:
                record["worker"] = message["worker"]
            if "result" in message:
                record["result"] = message["result"]
            return dict(record)

    def remove(self, worker_id: str, sock=None) -> None:
        with self._lock:
            current = self._by_id.get(worker_id)
            if current is None:
                return
            if sock is not None and current["connection"] is not sock:
                return
            del self._by_id[worker_id]

    def get(self, worker_id: str) -> dict | None:
        with self._lock:
            current = self._by_id.get(worker_id)
            return dict(current["record"]) if current else None

    def all(self) -> list[dict]:
        with self._lock:
            return [dict(item["record"]) for item in self._by_id.values()]

    def _record(self, worker_id: str, message: dict) -> dict:
        return {
            "id": worker_id,
            "worker": message.get("worker"),
            "result": message.get("result"),
        }


connections = Connection()
