import React, { useContext, useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate,nuseNavigate, useLocation } from "react-router-dom";
 import axios from "axios";
import API from "./api";
import { AuthContext } from "./context/AuthContext";
import "./styles/global.css";

// Component imports
import Login from "./components/Login";
import Sidebar from "./components/Sidebar";
import Guest_Management from "./components/Guest_Management";
import Bookings from "./components/Booking_Management";
import CheckInGuest from "./components/Checkin";
import CheckoutGuest from "./components/Checkout";
import Dashboard from "./components/Dashboard";
import Rooms from "./components/Rooms";
import Expenses from "./components/Expenses";  
import UserManager from "./components/User";
import Billing from "./components/Billing";
import Guestreport from "./components/guestreport";
// import Footer from "./components/Footer";

// 🏢 Top header with company name
function CompanyHeader() {
  const [companyName, setCompanyName] = useState("Loading...");
  const { clientId } = useContext(AuthContext);
 
  useEffect(() => {
    if (!clientId) return;
    API.get(`/meta/guesthouse/${clientId}`)
      .then((response) => setCompanyName(response.data.guesthouse_name))
      .catch(() => setCompanyName("Unknown Company"));
  }, [clientId]);

  return (
    <div style={{
      backgroundColor: "#004080",
      color: "white",
      padding: "10px 20px",
      fontSize: "1.5rem",
      fontWeight: "bold"
    }}>
      {companyName}
    </div>
  );
}

// 🧾 Footer component (inline)
function Footer() {
  return (
    <footer style={{
      textAlign: "center",
      padding: "10px",
      backgroundColor: "#f2f2f2",
      fontSize: "14px",
      color: "#555",
      borderTop: "1px solid #ddd",
      marginTop: "20px"
    }}>
      <p>
        <strong>Developed by Aarkay's Solutions | © 2025 SmartHost</strong>
      </p>
    </footer>
  );
}

// 💡 Main application logic after login
function MainApp() {
  const { token } = useContext(AuthContext);
  const [hasNavigated, setHasNavigated] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (token && location.pathname === "/") {
      navigate("/Sidebar");
    }
  }, [token]);
  if (!token || !clientId) return <Login />;

  const commonProps = { token, clientId };
}
  return (
    <>
      <CompanyHeader />
      <div style={{ display: "flex" }}>
        <div style={{ width: "220px", padding: "10px", backgroundColor: "#f5f5f5" }}>
          <Sidebar onNavigate={() => setHasNavigated(true)} />
        </div>
        <div style={{ padding: "10px", flex: 1 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/Sidebar" />} /> {/* ✅ Default redirect */}
            {!hasNavigated && (
              <Route path="*" element={<div>📋 Please select a module from the sidebar.</div>} />
            )}
            <Route path="/dashboard" element={<Dashboard {...commonProps} />} />
            <Route path="/rooms" element={<Rooms {...commonProps} />} />
            <Route path="/expenses" element={<Expenses {...commonProps} />} />
            <Route path="/user" element={<UserManager {...commonProps} />} />
            <Route path="/guest_management" element={<Guest_Management {...commonProps} />} />
            <Route path="/bookings" element={<Bookings {...commonProps} />} />
            <Route path="/checkin" element={<CheckInGuest {...commonProps} />} />
            <Route path="/checkout" element={<CheckoutGuest {...commonProps} />} />
            <Route path="/billing" element={<Billing {...commonProps} />} />
            <Route path="/guestreport" element={<Guestreport {...commonProps} />} />
            <Route path="*" element={<div>❌ Page Not Found</div>} />
          </Routes>
            <Footer /> {/* ✅ Inline footer added here */}
        </div>
      </div>
    </>
  );


// 🧭 Router wrapper
function App() {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  );
}
export default App;
