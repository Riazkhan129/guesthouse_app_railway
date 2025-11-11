import { useContext, useState, useEffect } from "react";
import { HashRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
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
import CheckInReport from "./components/Checkinreport";
import CheckoutGuest from "./components/Checkout";
import Dashboard from "./components/Dashboard";
import Rooms from "./components/Rooms";
import Expenses from "./components/Expenses";  
import UserManager from "./components/User";
import Billing from "./components/Billing";
import Guestreport from "./components/guestreport";
import Gueststayreport from "./components/Gusetstayreport";
import PerformanceReport from "./components/Performancereport";
import Expensecategories from "./components/Expensecategories";
import Expenseitems from "./components/Expenseitems";
import Roomservice from "./components/Roomservice";
import Contactus from "./components/Contactus";  
import PrivacyPolicy from "./components/PrivacyPolicy";
import { Link } from "react-router-dom";


// 🏢 Top header with company name test
function CompanyHeader() {
  const {
    token,
    clientId,
    companyName,
    companyLogo,
    setCompanyName,     // ✅ Use context setter
    setCompanyLogo      // ✅ Use context setter
  } = useContext(AuthContext);


  useEffect(() => {
    if (!clientId || !token) return;

     API.get(`/meta/guesthouse/${clientId}`, {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      })
        .then((res) => {
          console.log("API response:", res.data);

        // if (res.data?.guesthouse_name) {
          setCompanyName(res.data.guesthouse_name);
          setCompanyLogo(res.data?.logo || null);
      })
      .catch(() => {
        setCompanyName("Unknown Company")
        setCompanyLogo(null);
        });
   }, [clientId, token]);
  

  return (
    
    <div style={{
    backgroundColor: "#004080",
    color: "white",
    padding: "10px 20px",
    fontFamily: "sans-serif",
    display: "flex", // ✅ ADDED: Flex layout
    alignItems: "center",
    justifyContent: "space-between"
  }}>
    {/* ✅ Logo on the left */}
    {companyLogo ? (
      <img
        src={companyLogo}
        alt="Company Logo"
        style={{ maxHeight: "80px", objectFit: "contain" }}
      />
    ) : (
      <div style={{ height: "60px", width: "60px", backgroundColor: "#ccc", marginRight: "20px" }} />
    )}

    {/* ✅ Company name and tagline */}
    <div style={{ flexGrow: 1 }}>
      <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
        {companyName}
      </div>
      <div style={{ fontSize: "1rem", fontWeight: "normal", marginTop: "4px" }}>
        Powered by SmartHost — Know Your Numbers. Grow Your Business.
      </div>
    </div>
  </div>
)};


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
        <strong>Developed by Aarkay's Solutions | © 2025 SmartHost v2.0</strong>
      </p>
      <p style={{ fontStyle: "italic", marginTop: "4px" }}>
        Empowering guesthouse owners with financial clarity and full operational control.
      </p>
      <p style={{ marginTop: "8px" }}>
        <Link to="/contactus" style={{ color: "#004080", textDecoration: "none", marginRight: "10px" }}>
        Contact Us
      </Link>
      |
      <Link to="/privacy" style={{ color: "#004080", textDecoration: "none", marginLeft: "10px" }}>
        Privacy Policy
    </Link>
  </p>
    </footer>
  );
}

// 💡 Main application logic after login
function MainApp() {
  const { token, clientId } = useContext(AuthContext);
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
            <Route path="/Contactus" element={<Contactus {...commonProps} />} />
            <Route path="/privacy" element={<PrivacyPolicy {...commonProps} />} />
            <Route path="/dashboard" element={<Dashboard {...commonProps} />} />
            <Route path="/rooms" element={<Rooms {...commonProps} />} />
            <Route path="/expenses" element={<Expenses {...commonProps} />} />
            <Route path="/user" element={<UserManager {...commonProps} />} />
            <Route path="/guest_management" element={<Guest_Management {...commonProps} />} />
            <Route path="/bookings" element={<Bookings {...commonProps} />} />
            <Route path="/checkin" element={<CheckInGuest {...commonProps} />} />
            <Route path="/checkinreport" element={<CheckInReport {...commonProps} />} />
            <Route path="/checkout" element={<CheckoutGuest {...commonProps} />} />
            <Route path="/billing" element={<Billing {...commonProps} />} />
            <Route path="/guestreport" element={<Guestreport {...commonProps} />} />
            <Route path="/gueststayreport" element={<Gueststayreport {...commonProps} />} />
            <Route path="/Performancereport" element={<PerformanceReport {...commonProps} />} />
            <Route path="/Expensecategories" element={<Expensecategories {...commonProps} />} />
            <Route path="/Expenseitems" element={<Expenseitems {...commonProps} />} />
            <Route path="/Roomservice" element={<Roomservice {...commonProps} />} />
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
    <HashRouter>
      <MainApp />
    </HashRouter>
  )
}

export default App;