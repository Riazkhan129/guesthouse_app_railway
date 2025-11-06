import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import logo from './aarkayslogo.jpeg';


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
      {/* 🔧 Added logo + heading container */}
    <div style={{ display: "flex", alignItems: "center", marginBottom: "10px" }}>
      {/* 🔧 Logo image added here */}
      <img 
        src={logo} // 🔧 Make sure logo.jpeg is placed in the public folder
        alt="aarkys Logo" 
        style={{ height: "40px", marginRight: "10px" }} 
      />
      <h3 style={{ margin: 0 }}> SmartHost</h3>
    </div>
      <p>Logged in as: <strong>{username}</strong></p>
      <hr />
      {role === "Front Desk" ? (
        <>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/guest_management")}>👤 Guest Management</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/bookings")}>🗓️ Booking Management</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/checkin")}>✅ Check-In</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/Roomservice")}>📑 Room Service</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/checkinreport")}>✅ Check-In Report</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/checkout")}>🚪 Check-Out</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/gueststayreport")}>📑 Guest Stay Report</button>
        </>
      ) : (
        <>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/dashboard")}>📊 Dashboard</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/expenses")}>💸 Expenses</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/guestreport")}>📑 Reports</button>
          <h5 style={{ marginTop: '1.5rem', marginBottom: '0.5rem', fontWeight: 'bold' }}>Setup</h5>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/rooms")}>🛏️ Rooms</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/user")}>👥 Users</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/expensecategories")}>💸 Expense Categories</button>
          <button style={sidebarButtonStyle} onClick={() => handleClick("/expenseitems")}>💸 Expense Items</button>          
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
