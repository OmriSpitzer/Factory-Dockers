import asyncio
import json
import socket
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from connection import connections
from lib.env_funcs import get_env, load_env
from routes import bind_loop, notify, routes


load_env(Path(__file__).with_name(".env"))
WORKER_HOST = str(get_env("WORKER_HOST", "0.0.0.0"))
WORKER_PORT = int(get_env("WORKER_PORT", 7000))


class LineReader:
    def __init__(self, conn: socket.socket) -> None:
        self._conn = conn
        self._buf = b""

    def read(self) -> dict | None:
        while b"\n" not in self._buf:
            chunk = self._conn.recv(4096)
            if not chunk:
                return None
            self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        message = json.loads(line.decode())
        if not isinstance(message, dict):
            raise ValueError("expected a JSON object")
        return message


def send_json(conn: socket.socket, message: dict) -> None:
    conn.sendall(json.dumps(message).encode() + b"\n")


def handle_worker(conn: socket.socket) -> None:
    worker_id = ""
    registered = False
    try:
        reader = LineReader(conn)
        hello = reader.read()
        if not hello or "ack" not in hello:
            return
        worker_id = str(hello["ack"])
        send_json(conn, {"ack": worker_id})

        payload = reader.read()
        if not payload or str(payload.get("id")) != worker_id or "worker" not in payload:
            return
        connections.set(worker_id, conn, payload)
        registered = True
        notify()

        while True:
            message = reader.read()
            if message is None:
                break
            if str(message.get("id")) != worker_id:
                continue
            if "worker" not in message and "result" not in message:
                continue
            connections.update(worker_id, message)
            notify()
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    finally:
        if registered:
            connections.remove(worker_id, conn)
            notify()
        conn.close()


def serve_workers() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((WORKER_HOST, WORKER_PORT))
    listener.listen()
    while True:
        conn, _addr = listener.accept()
        threading.Thread(target=handle_worker, args=(conn,), daemon=True).start()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bind_loop(asyncio.get_running_loop())
    threading.Thread(target=serve_workers, daemon=True).start()
    yield


app = FastAPI(title="Factory API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes, prefix="/api")





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
