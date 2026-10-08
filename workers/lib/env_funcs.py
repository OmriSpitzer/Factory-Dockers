import argparse
import errno
import inspect
import os
import time
from pathlib import Path

"""
    Environment functions

    Attributes:
        None

    Methods:
        load_env(path: Path) -> None: Loads the environment variables from the given path
        get_env(key: str, default: str | int | None = None) -> str | int | None: Gets the environment variable with the given key
        client_host(host: str) -> str: Returns the client host
        next_port(port: int, start: int, connect_errno: int | None) -> int: Returns the next port
        run_worker(worker_cls: type, description: str) -> None: Runs the worker
"""

# Load the environment variables from the given path
def load_env(path: Path) -> None:
    # Check if the path exists
    if not path.exists():
        return

    # Read the environment variables from the path
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        # Split the line into key and value
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

# Get the environment variable with the given key
def get_env(key: str, default: str | int | None = None) -> str | int | None:
    return os.environ.get(key, default)

# Round robin port selection
def next_port(port: int, start: int, connect_errno: int | None) -> int:
    if connect_errno != errno.EADDRINUSE:
        return port
    return port + 1 if port < 65535 else start

# Run the worker
def run_worker(worker_cls: type, description: str) -> None:
    # Load the environment variables
    load_env(Path(inspect.getfile(worker_cls)).with_name(".env"))

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--host", default=get_env("SERVER_HOST", "DEFAULT_SERVER_HOST"))
    parser.add_argument("--port", type=int, default=int(get_env("SERVER_PORT", "DEFAULT_SERVER_PORT")))
    args = parser.parse_args()

    # Set the server host and port
    host = str(args.host)
    port = int(args.port)
    start = port
    os.environ["SERVER_HOST"] = host
    os.environ["SERVER_PORT"] = str(port)

    # Create the connection socket
    print(f"Connecting to {host}:{port}")
    worker = worker_cls()
    if worker._sock is not None:
        print(f"{worker.id} connected")
    else:
        print(f"{worker.id} waiting for server")

    # Connect to the server
    try:
        while True:
            if worker._sock is None:
                # Try the next port
                updated = next_port(port, start, worker._connect_errno)
                if updated != port:
                    port = updated
                    os.environ["SERVER_PORT"] = str(port)
                    print(f"port busy, retrying {host}:{port}")

                # Try to connect to the server
                worker.connect()
                if worker._sock is not None:
                    print(f"{worker.id} connected")
            time.sleep(2)
    except KeyboardInterrupt:
        print("stopped")
