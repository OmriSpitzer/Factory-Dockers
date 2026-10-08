import { useUI } from "../contexts/uiContext.tsx"
import Button from "./Button.tsx"

/**
 * Main header component
 */
const Header = ( 
  { onAddClient, onRemoveClient, hasClients }: 
  { onAddClient: () => void, onRemoveClient: () => void, hasClients: boolean }
) => {
  const { mode, toggleMode } = useUI() // UI mode (dark or light)

  return (
    <header 
      className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 border-b 
      border-border bg-bg px-4 py-4 sm:px-6"
    >
      {/* Left side - Factory name and description */}
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-text-h">My Factory</h1>
        <p className="mt-1 text-sm text-text">
          A factory floor where workers assemble, test, package, and ship products.
        </p>
      </div>

      {/* Right side - Client buttons */}
      <div className="flex items-center gap-3">
        {/* Remove client button */}
        {hasClients ? (
          <Button variant="danger" onClick={onRemoveClient}>
            Remove client
          </Button>
        ) : null}

        {/* Add client button */}
        <Button onClick={onAddClient}>
          Add client
        </Button>
      </div>

      {/* Theme toggle button */}
      <div className="flex justify-end">
        <Button variant="neutral" size="sm" onClick={toggleMode}>
          {mode === "dark" ? "Light" : "Dark"}
        </Button>
      </div>
    </header>
  )
}

export default Header
