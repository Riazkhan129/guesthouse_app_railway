import React, { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("");
  const [clientId, setClientId] = useState(null); // ✅ ADDED: Track client_id in context

  const login = (token, username, role, clientId) => {
    setToken(token);
    setUsername(username);
    setRole(role);
    setClientId(clientId); // ✅ ADDED: Save client_id in state

    localStorage.setItem("token", token);
    localStorage.setItem("username", username);
    localStorage.setItem("role", role);
    localStorage.setItem("client_id", clientId); // ✅ ADDED: Persist client_id for interceptors
  };

  const logout = () => {
    setToken("");
    setUsername("");
    setRole("");
    setClientId(null); // ✅ ADDED: Clear client_id from state

    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    localStorage.removeItem("client_id"); // ✅ ADDED: Remove client_id from storage
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        username,
        role,
        clientId, // ✅ ADDED: Expose client_id to consumers
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
