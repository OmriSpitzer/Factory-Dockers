// Get the workers
export const getWorkers = async () => {
  const response = await fetch("/api/worker")

  // Check if the response is ok
  if (!response.ok) throw new Error("worker request failed")

  return response.json()
}

// Subscribe to worker updates
export const subscribeWorkers = (onWorkers) => {
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
      if (payload.workers) onWorkers(payload.workers)
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
