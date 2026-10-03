import argparse
import errno
import inspect
import os
import time
from pathlib import Path


def load_env(path: Path) -> None:
    if not path.exists():
        return

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_env(key: str, default: str | int | None = None) -> str | int | None:
    return os.environ.get(key, default)


def client_host(host: str) -> str:
    if host == "0.0.0.0":
        return "127.0.0.1"
    return host


def next_port(port: int, start: int, connect_errno: int | None) -> int:
    if connect_errno != errno.EADDRINUSE:
        return port
    return port + 1 if port < 65535 else start


def run_worker(worker_cls: type, description: str) -> None:
    load_env(Path(inspect.getfile(worker_cls)).with_name(".env"))
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--host", default=get_env("SERVER_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(get_env("SERVER_PORT", 7000)))
    args = parser.parse_args()
    host = client_host(str(args.host))
    port = int(args.port)
    start = port
    os.environ["SERVER_HOST"] = host
    os.environ["SERVER_PORT"] = str(port)

    print(f"Connecting to {host}:{port}")
    worker = worker_cls()
    if worker._sock is not None:
        print(f"{worker.id} connected")
    else:
        print(f"{worker.id} waiting for server")

    try:
        while True:
            if worker._sock is None:
                updated = next_port(port, start, worker._connect_errno)
                if updated != port:
                    port = updated
                    os.environ["SERVER_PORT"] = str(port)
                    print(f"port busy, retrying {host}:{port}")
                worker.connect()
                if worker._sock is not None:
                    print(f"{worker.id} connected")
            time.sleep(2)
    except KeyboardInterrupt:
        print("stopped")
