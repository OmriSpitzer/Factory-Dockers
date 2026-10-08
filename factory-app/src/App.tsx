import { useLayoutEffect, useState } from "react"
import Header from "./components/Header.tsx"
import Footer from "./components/Footer.tsx"
import FactoryDisplay from "./components/FactoryDisplay.tsx"
import { useUI } from "./contexts/uiContext.tsx"
import type { Client } from "./types/client.tsx"

/**
 * Main application component
 */
const App = () => {
  const { mode } = useUI()                                   // UI mode (dark or light)
  const [clients, setClients] = useState<Client[]>([])        // List of clients

  // Set the UI mode
  useLayoutEffect(() => {
    document.documentElement.dataset.theme = mode
  }, [mode])

  // Add a client
  const addClient = async () => {
    const response = await fetch("/api/client", { method: "POST" })

    // Check if the response is ok
    if (!response.ok) throw new Error("add client failed")
    
    // Add the client to the list
    const client: Client = await response.json()
    const newClients = [...clients, client]
    setClients(newClients)

    console.log("Client added", client)
  }

  // Remove a client
  const removeClient = async () => {
    const response = await fetch("/api/client", { method: "DELETE" })

    // Check if the response is ok
    if (!response.ok) throw new Error("remove client failed")
    
    // Remove the client from the list
    const client: Client = await response.json()
    const newClients = clients.filter((item) => item.id !== client.id)
    setClients(newClients)

    console.log("Client removed", client)
  }

  return (
    <div className="flex h-screen flex-col bg-bg text-text">
      {/* Header */}
      <Header onAddClient={addClient} onRemoveClient={removeClient} hasClients={clients.length > 0} />

      {/* Main display */}
      <main className="flex min-h-0 flex-1 flex-col">
        <FactoryDisplay clients={clients} onClients={setClients} />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default App
