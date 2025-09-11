import React from "react";
import ReactDOM from "react-dom/client";
// import { HashRouter } from "react-router-dom";
import App from "./App.jsx";

// 🛡️ AuthProvider wraps your app with authentication logic
import { AuthProvider } from "./context/AuthContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* AuthProvider ensures your login logic is available across all routes */}
    <AuthProvider>
      {/* HashRouter avoids deep URL issues in Electron's file protocol */}
        <App />
    </AuthProvider>
  </React.StrictMode>
);
