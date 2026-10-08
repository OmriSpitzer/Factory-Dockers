import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from clients import ClientPool
from connection import connections
from objects.message import Message

"""
  API routes for the server

  Variables:
    routes: APIRouter - The API routes
    subscribers: set[WebSocket] - The subscribers to the server
    loop: asyncio.AbstractEventLoop | None - The event loop

  Functions:
"""

# Create the API routes
routes = APIRouter()

# Create the subscribers set
subscribers: set[WebSocket] = set()

# Create the event loop
loop: asyncio.AbstractEventLoop | None = None

# Create the client pool
client_pool = ClientPool()

# Bind the event loop
def bind_loop(running: asyncio.AbstractEventLoop) -> None:
    global loop
    loop = running


# Broadcast to the subscribers
async def _broadcast_to_subscribers() -> None:
    # Create the payload and mark the stale subscribers
    payload = {"workers": connections.all(), "clients": client_pool.all()}
    stale: list[WebSocket] = []

    # Send the payload to the subscribers
    for subscriber in list(subscribers):
        try:
            await subscriber.send_json(payload)
        except Exception:
            stale.append(subscriber)
    
    # Discard the stale subscribers
    for subscriber in stale:
        subscribers.discard(subscriber)


# Notify the subscribers
def notify() -> None:
    if loop is None:
        return
    
    # Broadcast to the subscribers
    asyncio.run_coroutine_threadsafe(_broadcast_to_subscribers(), loop)


# Read the root route
@routes.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Get a worker
@routes.get("/worker")
def get_worker(id: str | None = None):
    if id is None:
        return connections.all()
    worker = connections.get(id)
    if worker is None:
        raise HTTPException(status_code=404, detail="worker not found")
    return worker


# Put a worker
@routes.put("/worker")
def put_worker(message: Message):
    stored = connections.upsert(message.model_dump())
    notify()
    return stored


# Patch a worker
@routes.patch("/worker")
def patch_worker(patch: Message):
    fields = patch.model_dump(exclude={"id"}, exclude_none=True)
    stored = connections.update(patch.id, fields)
    if stored is None:
        raise HTTPException(status_code=404, detail="worker not found")
    notify()
    return stored


# Delete a worker
@routes.delete("/worker")
def delete_worker(id: str):
    if connections.get(id) is None:
        raise HTTPException(status_code=404, detail="worker not found")
    connections.remove(id)
    notify()
    return {"id": id}


# Add a client
@routes.post("/client")
def add_client():
    stored = client_pool.add()
    notify()
    return stored


# Remove a client
@routes.delete("/client")
def remove_client():
    stored = client_pool.remove_last()
    if stored is None:
        raise HTTPException(status_code=404, detail="client not found")
    notify()
    return stored


# Get the clients
@routes.get("/client")
def get_clients():
    return client_pool.all()


# Subscribe to the server
@routes.websocket("/subscribe")
async def subscribe(websocket: WebSocket):
    await websocket.accept()
    subscribers.add(websocket)
    await websocket.send_json({"workers": connections.all(), "clients": client_pool.all()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscribers.discard(websocket)
