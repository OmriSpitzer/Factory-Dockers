import json
import socket

"""
  Socket IO functions
  
  Functions:
    write_json(sock: socket.socket, message: dict) -> None: Writes a JSON message to the socket
    read_json(sock: socket.socket) -> dict | None: Reads a JSON message from the socket
    publish(sock: socket.socket | None, message: dict) -> socket.socket | None: Publishes a message to the socket
"""

# Write a JSON message to the socket
def write_json(sock: socket.socket, message: dict) -> None:
    json_message = json.dumps(message).encode() + b"\n"
    sock.sendall(json_message)

# Read a JSON message from the socket
def read_json(sock: socket.socket) -> dict | None:
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buf += chunk
    
    # Create the line
    line = buf.split(b"\n", 1)[0]
    return json.loads(line.decode())

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
