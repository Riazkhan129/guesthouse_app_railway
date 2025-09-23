import React, { useContext } from "react";
// import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Sidebar({ onNavigate }) {
  const { role, username, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleClick = (path) => {
    navigate(path);
    onNavigate(true);
  };

  const handleLogout = () => {
    // 🔧 UPDATED: Clear session and local storage
    sessionStorage.clear();
    localStorage.clear();

    // 🔧 UPDATED: Reset navigation state
    onNavigate(false);

    // 🔧 UPDATED: Call logout logic from context
    logout();

    // 🔧 UPDATED: Redirect to login screen
    navigate("/login", { replace: true });
  };
  const sidebarButtonStyle = {
    display: "block",
    width: "100%",
    padding: "8px 10px",
    margin: "4px 0",
    textAlign: "left",
    backgroundColor: "transparent",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "15px",
    color: "#333",
    fontFamily: "inherit",
  };

  return (
    <div style={{ width: "100%", fontFamily: "Arial", padding: "10px" }}>
      <h3>🏨 SmartHost</h3>
      <p>Logged in as: <strong>{username}</strong></p>
      <hr />
      {role === "Front Desk" ? (
        <>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/guest_management")}>👤 Guest Management</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/bookings")}>🗓️ Booking Management</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/checkin")}>✅ Check-In</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/checkout")}>🚪 Check-Out</button>
        </>
      ) : (
        <>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/dashboard")}>📊 Dashboard</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/rooms")}>🛏️ Rooms</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/expenses")}>💸 Expenses</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/user")}>👥 Users</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/guestreport")}>📑 Reports</button>
        </>
      )}
      <br />
      <button style={sidebarButtonStyle} onClick={() => { logout(); onNavigate(false); }}>
        🔓 Logout
      </button>
    </div>
  );
}

export default Sidebar;
