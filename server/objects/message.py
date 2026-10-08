from pydantic import BaseModel
from typing import Any

"""
  Message base class for the connection
"""
class Message(BaseModel):
    id: str
    worker: dict
    result: Any = None