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
from lib.socket_io import read_json, write_json
from routes import bind_loop, notify, routes

"""
  Server main script

  Variables:
    LISTEN_HOST: str - The host to listen on
    LISTEN_PORT: int - The port to listen on
    app: FastAPI - The FastAPI app

  Functions:
    handle_worker(conn: socket.socket) -> None: Handle the worker connection
    serve_workers() -> None: Serve the workers
    lifespan(_app: FastAPI) -> AsyncGenerator[None, None]: Lifespan
"""

# Load the environment variables
load_env(Path(__file__).with_name(".env"))
LISTEN_HOST = str(get_env("LISTEN_HOST", "DEFAULT_LISTEN_HOST"))
LISTEN_PORT = int(get_env("LISTEN_PORT", "DEFAULT_LISTEN_PORT"))

# Handle the worker connection
def handle_worker(conn: socket.socket) -> None:
    worker_id = ""
    registered = False

    try:
        # Get an Ack from the worker
        hello = read_json(conn)
        if not hello or "ack" not in hello:
            return

        # Get Ack data and send an Ack back
        worker_id = str(hello["ack"])
        write_json(conn, {"ack": worker_id})

        # Get the worker payload and register the worker
        payload = read_json(conn)
        if not payload or str(payload.get("id")) != worker_id or "worker" not in payload:
            return
        
        # Register the worker
        connections.set(worker_id, conn, payload)
        registered = True
        notify()

        while True:
            # Read a message from the worker
            message = read_json(conn)
            if message is None:
                break
            if str(message.get("id")) != worker_id:
                continue
            if "worker" not in message and "result" not in message:
                continue

            # Update the worker's connection and notify the clients
            connections.update(worker_id, message)
            notify()
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    finally:
        # Remove the worker and close the connection
        if registered:
            connections.remove(worker_id, conn)
            notify()
        conn.close()


# Serve the workers
def serve_workers() -> None:
    # Create the listener socket
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((LISTEN_HOST, LISTEN_PORT))
    listener.listen()

    # Serve the workers
    while True:
        conn, _addr = listener.accept()

        # Create a new thread to handle the worker
        threading.Thread(target=handle_worker, args=(conn,), daemon=True).start()


# Lifespan
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Bind the event loop
    bind_loop(asyncio.get_running_loop())
    threading.Thread(target=serve_workers, daemon=True).start()
    yield


# Create the FastAPI app
app = FastAPI(title="Factory API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes, prefix="/api")

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
