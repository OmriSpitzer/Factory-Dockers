from abc import ABC, abstractmethod
import base64
import inspect
import json
import socket
import time
from pathlib import Path
from typing import Any

from workers.lib.env_funcs import client_host, get_env, load_env

class BaseWorker(ABC):
    def __init__(self, id: str, timeout: int = 10):
      self.id = id
      self.status = "idle"
      self._progress = 0
      self._timeout = timeout
      self._sock: socket.socket | None = None
      self._connect_errno: int | None = None
      self._result = None
      self.image = self._load_image()
      load_env(Path(inspect.getfile(type(self))).with_name(".env"))
      self.connect()

    @abstractmethod
    def returned_product(self, product: Any) -> Any:
        pass

    def work(self, input: Any) -> Any:
      self.status = "working"
      self._progress = 0
      self._publish()
      for i in range(self._timeout):
        time.sleep(1)
        self._progress = i+1
        self._send_progress()

      self.status = "idle"
      result = self.returned_product(input)
      self._result = self._jsonable(result)
      self._publish()
      return result
    
    def _send_progress(self):
      print(f"Progress: {self._progress}/{self._timeout}")
      self._publish()

    def _payload(self) -> dict:
      return {
        "id": self.id,
        "worker": self.snapshot(),
        "result": self._result,
      }

    def _jsonable(self, value: Any) -> Any:
      if value is None or isinstance(value, (str, int, float, bool)):
        return value
      if isinstance(value, dict):
        return {key: self._jsonable(item) for key, item in value.items()}
      if isinstance(value, (list, tuple)):
        return [self._jsonable(item) for item in value]
      data = {
        key: self._jsonable(item)
        for key, item in vars(value).items()
        if not key.startswith("_")
      }
      data["type"] = type(value).__name__
      return data

    def _load_image(self) -> str:
      folder = Path(inspect.getfile(type(self))).parent
      matches = sorted(folder.glob("*_img.png"))
      if not matches:
        return ""
      encoded = base64.b64encode(matches[0].read_bytes()).decode("ascii")
      return f"data:image/png;base64,{encoded}"

    def snapshot(self) -> dict:
      return {
        "id": self.id,
        "type": self.id.split("-", 1)[0].lower(),
        "status": self.status,
        "progress": self._progress,
        "timeout": self._timeout,
        "image": self.image,
      }

    def connect(self, host: str | None = None, port: int | None = None) -> None:
      host = client_host(str(get_env("SERVER_HOST", "127.0.0.1")) if host is None else host)
      port = int(get_env("SERVER_PORT", 7000)) if port is None else port
      self._connect_errno = None
      sock: socket.socket | None = None
      try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.settimeout(2)
        self._write(sock, {"ack": self.id})
        reply = self._read(sock)
        if not isinstance(reply, dict) or reply.get("ack") != self.id:
          sock.close()
          return
        sock.settimeout(None)
        self._sock = sock
        self._write(sock, self._payload())
      except OSError as exc:
        self._connect_errno = exc.errno
        if sock is not None and self._sock is not sock:
          sock.close()
        self._sock = None

    def _publish(self) -> None:
      if self._sock is None:
        return
      try:
        self._write(self._sock, self._payload())
      except OSError:
        self._sock = None

    def _write(self, sock: socket.socket, message: dict) -> None:
      sock.sendall(json.dumps(message).encode() + b"\n")

    def _read(self, sock: socket.socket) -> dict | None:
      buf = b""
      while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
          return None
        buf += chunk
      line = buf.split(b"\n", 1)[0]
      return json.loads(line.decode())
    