import { useLayoutEffect, useState } from "react"
import Header from "./components/Header.tsx"
import Footer from "./components/Footer.tsx"
import FactoryDisplay from "./components/FactoryDisplay.tsx"
import { useUI } from "./contexts/uiContext.tsx"
import type { Client } from "./types/client.tsx"
import { addClient as createClient, removeClient as deleteClient } from "./services/clientService.js"

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
    const client: Client = await createClient()

    // Add the client to the list
    const newClients = [...clients, client]
    setClients(newClients)

    console.log("Client added", client)
  }

  // Remove a client
  const removeClient = async () => {
    const client: Client = await deleteClient()

    // Remove the client from the list
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
