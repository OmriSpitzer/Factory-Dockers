import { useLayoutEffect, useState } from "react"
import Header from "./components/Header.tsx"
import Footer from "./components/Footer.tsx"
import FactoryDisplay from "./components/FactoryDisplay.tsx"
import { useUI } from "./contexts/uiContext.tsx"
import type { Client } from "./types/client.tsx"

const App = () => {
  const { mode } = useUI()
  const [clients, setClients] = useState<Client[]>([])

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = mode
  }, [mode])

  const addClient = () => {
    fetch("/api/client", { method: "POST" })
      .then((response) => {
        if (!response.ok) throw new Error("add client failed")
        return response.json()
      })
      .then((client: Client) => {
        setClients((current) => current.some((item) => item.id === client.id) ? current : [...current, client])
      })
      .catch(() => {})
  }

  const removeClient = () => {
    fetch("/api/client", { method: "DELETE" })
      .then((response) => {
        if (!response.ok) throw new Error("remove client failed")
        return response.json()
      })
      .then((client: Client) => {
        setClients((current) => current.filter((item) => item.id !== client.id))
      })
      .catch(() => {})
  }

  return (
    <div className="flex h-screen flex-col bg-bg text-text">
      <Header onAddClient={addClient} onRemoveClient={removeClient} hasClients={clients.length > 0} />
      <main className="flex min-h-0 flex-1 flex-col">
        <FactoryDisplay clients={clients} onClients={setClients} />
      </main>
      <Footer />
    </div>
  )
}

export default App
