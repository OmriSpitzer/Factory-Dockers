import { useUI } from "../contexts/uiContext.tsx"

const Header = ({
  onAddClient,
  onRemoveClient,
  hasClients,
}: {
  onAddClient: () => void
  onRemoveClient: () => void
  hasClients: boolean
}) => {
  const { mode, toggleMode } = useUI()

  return (
    <header className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 border-b border-border bg-bg px-4 py-4 sm:px-6">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-text-h">My Factory</h1>
        <p className="mt-1 text-sm text-text">
          A factory floor where workers assemble, test, package, and ship products.
        </p>
      </div>
      <div className="flex items-center gap-3">
        {hasClients ? (
          <button
            type="button"
            onClick={onRemoveClient}
            className="rounded-full bg-[#dc2626] px-5 py-2 text-base font-medium text-white shadow-sm transition duration-150 hover:-translate-y-0.5 hover:bg-[#b91c1c] hover:shadow-md"
          >
            Remove client
          </button>
        ) : null}
        <button
          type="button"
          onClick={onAddClient}
          className="rounded-full bg-[#16a34a] px-5 py-2 text-base font-medium text-white shadow-sm transition duration-150 hover:-translate-y-0.5 hover:bg-[#15803d] hover:shadow-md"
        >
          Add client
        </button>
      </div>
      <div className="flex justify-end">
        <button
          type="button"
          onClick={toggleMode}
          className="rounded-full border border-border bg-code-bg px-3.5 py-1.5 text-sm font-medium text-text-h shadow-sm transition duration-150 hover:-translate-y-0.5 hover:bg-border hover:shadow-md"
        >
          {mode === "dark" ? "Light" : "Dark"}
        </button>
      </div>
    </header>
  )
}

export default Header
