import React, { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("");
  const [clientId, setClientId] = useState(null); 
  const [companyName, setCompanyName] = useState(""); // ✅ NEW: Track company name
  const [companyLogo, setCompanyLogo] = useState(null); // ✅ NEW: Track logo as base64

  const login = (token, username, role, clientId) => {
    setToken(token);
    setUsername(username);
    setRole(role);
    setClientId(clientId); // ✅ ADDED: Save client_id in state

    localStorage.setItem("token", token);
    localStorage.setItem("username", username);
    localStorage.setItem("role", role);
    localStorage.setItem("client_id", clientId); 
  };

  const logout = () => {
    setToken("");
    setUsername("");
    setRole("");
    setClientId(null); 
    setCompanyName(""); // ✅ Clear company name
    setCompanyLogo(null); // ✅ Clear logo

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
        clientId,
        companyName,       // ✅ Expose company name
        companyLogo,       // ✅ Expose logo
        setCompanyName,    // ✅ Setter for name
        setCompanyLogo,    // ✅ Setter for logo
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
