import React, { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("");
  const [clientId, setClientId] = useState(null);

  const login = (token, username, role, clientId) => {
    setToken(token);
    setUsername(username);
    setRole(role);
    setClientId(clientId);
    localStorage.setItem("token", token);
    localStorage.setItem("username", username);
    localStorage.setItem("role", role);
  };

  const logout = () => {
    setToken("");
    setUsername("");
    setRole("");
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
  };

  return (
    <AuthContext.Provider value={{ token, username, role, login, clientId, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
