import json
import socket

"""
  Socket IO functions
  
  Functions:
    write_json(sock: socket.socket, message: dict) -> None: Writes a JSON message to the socket
    read_json(sock: socket.socket) -> dict | None: Reads a JSON message from the socket
    publish(sock: socket.socket | None, message: dict) -> socket.socket | None: Publishes a message to the socket
"""

# Leftover bytes per socket. socket.socket cannot store attributes.
_rxbufs: dict[int, bytes] = {}

# Write a JSON message to the socket
def write_json(sock: socket.socket, message: dict) -> None:
    json_message = json.dumps(message).encode() + b"\n"
    sock.sendall(json_message)

# Read a JSON message from the socket
def read_json(sock: socket.socket) -> dict | None:
    key = id(sock)
    buf = _rxbufs.pop(key, b"")
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buf += chunk
    
    # Create the line
    line, rest = buf.split(b"\n", 1)
    if rest:
        _rxbufs[key] = rest
    message = json.loads(line.decode())
    if not isinstance(message, dict):
        raise ValueError("expected a JSON object")
    return message

# Publish a message to the socket
def publish(sock: socket.socket | None, message: dict) -> socket.socket | None:
    # Check if the socket exists
    if sock is None:
        return None
    
    # Try to write the message to the socket
    try:
        write_json(sock, message)
    except OSError:
        return None
    return sock
