// Get the clients
export const getClients = async () => {
  const response = await fetch("/api/client")

  // Check if the response is ok
  if (!response.ok) throw new Error("client request failed")

  return response.json()
}

// Add a client
export const addClient = async () => {
  const response = await fetch("/api/client", { method: "POST" })

  // Check if the response is ok
  if (!response.ok) throw new Error("add client failed")

  return response.json()
}

// Remove a client
export const removeClient = async () => {
  const response = await fetch("/api/client", { method: "DELETE" })

  // Check if the response is ok
  if (!response.ok) throw new Error("remove client failed")

  return response.json()
}

// Subscribe to client updates
export const subscribeClients = (onClients) => {
  let socket = null
  let retry
  let closed = false

  const connect = () => {
    if (closed) return
    const protocol = location.protocol === "https:" ? "wss" : "ws"
    socket = new WebSocket(`${protocol}://${location.host}/api/subscribe`)
    socket.onmessage = (event) => {
      if (closed) return
      const payload = JSON.parse(event.data)
      if (payload.clients) onClients(payload.clients)
    }
    socket.onclose = () => {
      if (closed) return
      retry = setTimeout(connect, 1000)
    }
  }

  connect()

  return () => {
    closed = true
    clearTimeout(retry)
    socket?.close()
  }
}
