from abc import ABC, abstractmethod
import base64
import inspect
import socket
import time
from pathlib import Path
from typing import Any

from workers.lib.env_funcs import get_env, load_env
from workers.lib.socket_io import publish, read_json, write_json

"""
  Base class for all workers

  Attributes:
    id: str - The worker's unique identifier
    status: str - The worker's current status ("idle", "working", "done")
    _progress: int - The current progress of the worker
    _timeout: int - The time in seconds the worker will work
    _sock: socket.socket | None - The socket connection to the server
    _connect_errno: int | None - The error code if the connection fails
    _result: Any | None - The result of the worker's work
    image: str - The image of the worker

  Methods:
    returned_product(self, product: Any) -> Any : Abstract method to be implemented by subclasses to return the product
    work(self, input: Any) -> Any: Works on the given input and returns the result
    snapshot(self) -> dict: Returns a snapshot of the worker's status, progress, timeout, and image
    connect(self, host: str | None = None, port: int | None = None) -> None: Connects the worker to the server
"""
class BaseWorker(ABC):
    def __init__(self, id: str, timeout: int = 10) -> None:
      # Metadata attributes
      self.id: str = id
      self.status: str = "idle"
      self.progress: int = 0
      self.timeout: int = timeout
      self.result: Any | None = None
      self.image: str = self._load_image()

      # Connection attributes
      self._sock: socket.socket | None = None
      self._connect_errno: int | None = None
      
      # Load environment variables and connect to the server
      load_env(Path(inspect.getfile(type(self))).with_name(".env"))
      self.connect()

    # Returned product from the worker
    @abstractmethod
    def returned_product(self, product: Any) -> Any:
        pass

    # Work on the given input and return the result
    def work(self, input: Any) -> Any:
      # Set worker as not idle
      self.status = "working"
      self.progress = 0
      self._sock = publish(self._sock, self._payload())

      # Work and send progress to the server
      for i in range(self.timeout):
        time.sleep(1)
        self.progress = i+1
        self._send_progress()

      # Set worker as idle and return the result to the server
      self.status = "idle"
      result = self.returned_product(input)
      self.result = self._jsonable(result)
      self._sock = publish(self._sock, self._payload())
      return result

    # Connect to the server
    def connect(self, host: str | None = None, port: int | None = None) -> None:
      # Get the server host and port
      host = str(get_env("SERVER_HOST", "DEFAULT_SERVER_HOST")) if host is None else host
      port = int(get_env("SERVER_PORT", "DEFAULT_SERVER_PORT")) if port is None else port

      # Create the connection socket
      self._connect_errno = None
      sock: socket.socket | None = None

      # Try to connect to the server
      try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.settimeout(2)

        # Send the ack message to the server
        write_json(sock, {"ack": self.id})
        reply = read_json(sock)

        # Check if the server acknowledged the message
        if not isinstance(reply, dict) or reply.get("ack") != self.id:
          sock.close()
          return
        sock.settimeout(None)

        # Set the connection socket and send the payload to the server
        self._sock = sock
        write_json(sock, self._payload())
      except OSError as exc:
        self._connect_errno = exc.errno
        if sock is not None and self._sock is not sock:
          sock.close()
        self._sock = None
    
    # Send the progress to the server
    def _send_progress(self) -> None:
      print(f"Progress: {self.progress}/{self.timeout}")
      self._sock = publish(self._sock, self._payload())

    # Create the payload for the server
    def _payload(self) -> dict:
      return {
        "id": self.id,
        "worker": self.to_dict(),
        "result": self.result,
      }

    # Convert the worker to a dictionary
    @abstractmethod
    def to_dict(self) -> dict:
      return {
        "id": self.id,
        "type": self.id.split("-", 1)[0].lower(),
        "status": self.status,
        "progress": self.progress,
        "timeout": self.timeout,
        "image": self.image,
      }

    # Load the image from the worker's folder
    def _load_image(self) -> str:
      folder = Path(inspect.getfile(type(self))).parent
      matches = sorted(folder.glob("*_img.png"))
      if not matches:
        return ""
      encoded = base64.b64encode(matches[0].read_bytes()).decode("ascii")
      return f"data:image/png;base64,{encoded}"
