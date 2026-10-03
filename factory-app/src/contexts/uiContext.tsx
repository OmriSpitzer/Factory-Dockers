import { useState, createContext, useContext } from "react";

type UIContextValue = {
    mode: "dark" | "light";
    toggleMode: () => void;
};

const UIContext = createContext<UIContextValue>({
    mode: "light",
    toggleMode: () => {},
});

export const useUI = () => {
    return useContext(UIContext);
};

export const UIProvider = ({ children }: { children: React.ReactNode }) => {
    const [mode, setMode] = useState<"dark" | "light">("light");

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
