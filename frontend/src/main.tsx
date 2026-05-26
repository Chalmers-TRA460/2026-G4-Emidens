import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./app/App.tsx";
import { ActiveRunProvider } from "./app/ActiveRunContext";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <ActiveRunProvider>
      <App />
    </ActiveRunProvider>
  </BrowserRouter>
);
