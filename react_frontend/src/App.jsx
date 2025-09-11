import React, { useContext, useState, useEffect } from "react";
import { BrowserRouter } from "react-router-dom";

import {
  // BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation
} from "react-router-dom";
import axios from "axios";
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
import Expenses from "./components/Expenses";  // ✅ Fixed typo here
import UserManager from "./components/User";
import Billing from "./components/Billing";
import Guestreport from "./components/guestreport";
// import Footer from "./components/Footer";

const API_URL = "http://localhost:8000";

// 🏢 Top header with company name
function CompanyHeader() {
  const [companyName, setCompanyName] = useState("Loading...");

  useEffect(() => {
    axios.get(`${API_URL}/meta/guesthouse`)
      .then((response) => setCompanyName(response.data.guesthouse_name))
      .catch(() => setCompanyName("Unknown Company"));
  }, []);

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
        <strong>Developed by Aarkay's Solutions | © 2025 LodgeControl</strong>
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

//  useEffect(() => {
//    if (token && location.pathname === "/") {
//      navigate("/dashboard");  // ✅ Default redirect after login
//    }
//  }, [token]);

  if (!token) return <Login />;

  return (
    <>
      <CompanyHeader />
      <div style={{ display: "flex" }}>
        <div style={{ width: "220px", padding: "10px", backgroundColor: "#f5f5f5" }}>
          <Sidebar onNavigate={() => setHasNavigated(true)} />
        </div>
        <div style={{ padding: "10px", flex: 1 }}>
          <Routes>
            {!hasNavigated && (
              <Route path="*" element={<div>📋 Please select a module from the sidebar.</div>} />
            )}
            <Route path="/dashboard" element={<Dashboard API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/rooms" element={<Rooms API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/expenses" element={<Expenses API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/user" element={<UserManager API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/guest_management" element={<Guest_Management API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/bookings" element={<Bookings API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/checkin" element={<CheckInGuest API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/checkout" element={<CheckoutGuest API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/billing" element={<Billing API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />
            <Route path="/guestreport" element={<Guestreport API_URL={API_URL} headers={{ Authorization: `Bearer ${token}` }} />} />            
            <Route path="*" element={<div>❌ Page Not Found</div>} />
          </Routes>
            <Footer /> {/* ✅ Inline footer added here */}
        </div>
      </div>
    </>
  );
}

// 🧭 Router wrapper
function App() {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  );
}
export default App;
