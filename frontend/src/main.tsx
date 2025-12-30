import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { DreamCacheProvider } from "./contexts/DreamCacheContext";
import "~/styles/globals.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <DreamCacheProvider>
          <App />
        </DreamCacheProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
