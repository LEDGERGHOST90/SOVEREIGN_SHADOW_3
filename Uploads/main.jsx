import React from "react";
import { createRoot } from "react-dom/client";
import NexusApp from "./App.jsx";
import "./index.css";

const root = createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <NexusApp />
  </React.StrictMode>
);
