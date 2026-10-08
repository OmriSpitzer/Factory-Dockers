import { useState, createContext, useContext } from "react";

/**
 * UI context
 * 
 * Visual user interface for the application
 */

// UI context value type
type UIContextValue = {
    mode: "dark" | "light";
    toggleMode: () => void;
};

// Create the UI context
const UIContext = createContext<UIContextValue>({
    mode: "light",
    toggleMode: () => {},
});

// Use the UI context
export const useUI = () => useContext(UIContext);

// UI provider
export const UIProvider = ({ children }: { children: React.ReactNode }) => {
    const [mode, setMode] = useState<"dark" | "light">("light"); // UI mode (dark or light)

    // Toggle the UI mode
    const toggleMode = () => {
        const newMode = mode === "dark" ? "light" : "dark";
        setMode(newMode);
    };

    return (
        <UIContext.Provider value={{ mode, toggleMode }}>
            {children}
        </UIContext.Provider>
    );
};
