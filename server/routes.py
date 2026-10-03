import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from clients import threads
from connection import connections


routes = APIRouter()
subscribers: set[WebSocket] = set()
loop: asyncio.AbstractEventLoop | None = None


class WorkerMessage(BaseModel):
    id: str
    worker: dict
    result: Any = None


class WorkerPatch(BaseModel):
    id: str
    worker: dict | None = None
    result: Any = None


def bind_loop(running: asyncio.AbstractEventLoop) -> None:
    global loop
    loop = running


async def broadcast() -> None:
    payload = {"workers": connections.all(), "clients": threads.all()}
    stale: list[WebSocket] = []
    for subscriber in list(subscribers):
        try:
            await subscriber.send_json(payload)
        except Exception:
            stale.append(subscriber)
    for subscriber in stale:
        subscribers.discard(subscriber)


def notify() -> None:
    if loop is None:
        return
    asyncio.run_coroutine_threadsafe(broadcast(), loop)


@routes.get("/")
def read_root():
    return {"message": "Hello, World!"}


@routes.get("/worker")
def get_worker(id: str | None = None):
    if id is None:
        return connections.all()
    worker = connections.get(id)
    if worker is None:
        raise HTTPException(status_code=404, detail="worker not found")
    return worker


@routes.put("/worker")
def put_worker(message: WorkerMessage):
    stored = connections.upsert(message.model_dump())
    notify()
    return stored


@routes.patch("/worker")
def patch_worker(patch: WorkerPatch):
    fields = patch.model_dump(exclude={"id"}, exclude_none=True)
    stored = connections.update(patch.id, fields)
    if stored is None:
        raise HTTPException(status_code=404, detail="worker not found")
    notify()
    return stored


@routes.delete("/worker")
def delete_worker(id: str):
    if connections.get(id) is None:
        raise HTTPException(status_code=404, detail="worker not found")
    connections.remove(id)
    notify()
    return {"id": id}


@routes.post("/client")
def add_client():
    stored = threads.add()
    notify()
    return stored


@routes.delete("/client")
def remove_client():
    stored = threads.remove_last()
    if stored is None:
        raise HTTPException(status_code=404, detail="client not found")
    notify()
    return stored


@routes.get("/client")
def get_clients():
    return threads.all()


@routes.websocket("/subscribe")
async def subscribe(websocket: WebSocket):
    await websocket.accept()
    subscribers.add(websocket)
    await websocket.send_json({"workers": connections.all(), "clients": threads.all()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscribers.discard(websocket)
