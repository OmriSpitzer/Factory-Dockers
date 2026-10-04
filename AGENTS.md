# Worker Pool

A factory-floor app. Python workers assemble, test, package, and ship products, and a React dashboard shows them live next to waiting clients.

## Layout

- `server/` — FastAPI app (`server.py`) on port 8000. Routes live in `routes.py` under `/api`. A background thread accepts worker sockets on port 7000 (`WORKER_HOST` / `WORKER_PORT` in `server/.env`).
- `workers/` — `BaseWorker` plus one process per stage: `assemble`, `testing`, `package`, `shipping`. Each stage loads its own `.env` and is started with `python -m` on that module. Shared objects are in `workers/objects/`.
- `factory-app/` — Vite + React + TypeScript + Tailwind. The dev server proxies `/api` (including WebSocket) to `localhost:8000`.

## Flow

1. A worker connects, sends `{"ack": "<id>"}`, and waits for the same ack back. Its id prefix is the type (`ASSEMBLER-`, `TESTER-`, `PACKAGER-`, `SHIPPER-`).
2. It then sends newline-delimited JSON: `id`, a `worker` snapshot (`status`, `progress`, `timeout`, `image`), and an optional `result`.
3. `work()` sleeps for `timeout` seconds, publishing progress each second, then calls `returned_product()`.
4. The server stores the connection and broadcasts `{ workers, clients }` to `/api/subscribe`.
5. `FactoryDisplay` loads `/api/worker` and `/api/client`, then keeps both lists in sync from that socket. Columns are Clients, then assembler, tester, packager, shipper. Card order is local drag-and-drop state.
6. Add client / Remove client hit `POST` and `DELETE /api/client`. Clients are daemon threads with a random name and a 5–10s timeout.

## Boundaries

- Do not change existing comments. Leave comment text, placement, and surrounding blank lines as they are.
- Change only the files the task needs. Leave `.env` files, images, and generated caches alone.
- Keep the worker wire format: one JSON object per line, ack handshake, then `id` / `worker` / `result`.
- Keep the dashboard column order: clients, assembler, tester, packager, shipper.
- Match the style already in the file you edit (Python indentation, React function components, Tailwind classes).
