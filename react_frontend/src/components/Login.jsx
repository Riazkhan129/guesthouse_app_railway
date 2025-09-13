import React, { useEffect, useRef, useState, useContext} from "react";
import axios from "axios";
import qs from "qs";
import { AuthContext } from "../context/AuthContext";
function Login() {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [clientId, setClientId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const usernameRef = useRef(null);

  useEffect(() => {
    if (usernameRef.current) {
      usernameRef.current.focus(); // focus on username when screen opens
    }
  }, []);

  const handleLogin = async () => {
  setLoading(true);
  setError("");

  const API_URL = import.meta.env.VITE_API_BASE_URL;
  console.log("🔍 API Base URL:", API_URL);
  console.log("📡 Sending login request to:", `${API_URL}/token`);
  console.log("📝 Login payload:", { username, password, client_id: clientId });

  try {
    const res = await axios.post(
      `${API_URL}/token`,
      qs.stringify({ username, password, client_id: clientId }),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    console.log("✅ Login response:", res.data);
    login(res.data.access_token, username, res.data.role);
  } catch (err) {
    console.error("❌ Login error:", err.response?.data || err.message);
    setError("Invalid username, password or client id.");
    setPassword("");
  } finally {
    setLoading(false);
  }
};


  return (
    <div style={{
      maxWidth: "400px",
      margin: "50px auto",
      padding: "20px",
      border: "1px solid #ccc",
      borderRadius: "8px",
      boxShadow: "0 2px 5px rgba(0,0,0,0.1)"
    }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>🔐 Login</h2>

      {error && (
        <div style={{ 
          backgroundColor: "#ffe6e6", 
          color: "#cc0000", 
          padding: "10px", 
          marginBottom: "15px", 
          borderRadius: "4px", 
          textAlign: "center" 
        }}>
          {error}
        </div>
      )}

      {/* ✅ NEW: Client ID input */}
      <input
        value={clientId}
        onChange={(e) => setClientId(e.target.value)}
        placeholder="Client ID"
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "10px",
          border: "1px solid #aaa",
          borderRadius: "4px"
        }}
      />
      
      <input
        ref={usernameRef}
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "10px",
          border: "1px solid #aaa",
          borderRadius: "4px"
        }}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        style={{
          width: "100%",
          padding: "10px",
          marginBottom: "20px",
          border: "1px solid #aaa",
          borderRadius: "4px"
        }}
      />
      <button
        onClick={handleLogin}
        disabled={loading}
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: loading ? "#9E9E9E" : "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
      >
        {loading ? "Logging in..." : "🔑 Login"}
      </button>
    </div>
  );
}

export default Login;
