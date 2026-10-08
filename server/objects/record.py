from dataclasses import dataclass
from typing import Any
import socket

"""
  Record class for the connection
"""

# The record connection class
@dataclass(slots=True, frozen=True)
class Record:
    id: str
    worker: dict | None = None
    result: Any = None

# The entry class for the connection
@dataclass(slots=True)
class Entry:
    connection: socket.socket | None
    record: Record