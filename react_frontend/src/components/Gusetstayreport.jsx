import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

const GuestStayReport = () => {
  const { token, clientId } = useContext(AuthContext);

  const [guests, setGuests] = useState([]);
  const [selectedNic, setSelectedNic] = useState("");
  const [guest, setGuest] = useState({});
  const [bookings, setBookings] = useState([]);
  const [runtime, setRuntime] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [companyLogo, setCompanyLogo] = useState([]);
  const [companyName, setCompanyName] = useState("Loading...");
  const totalPages = Math.ceil(bookings.length / 15);

  useEffect(() => {
    if (!clientId || !token) return;

    API.get(`/meta/guesthouse/${clientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => {
        setCompanyName(res.data?.guesthouse_name || "Unknown Company");
        setCompanyLogo(res.data?.logo || null);
      })
      .catch(() => setCompanyName("Unknown Company"));
  }, [clientId, token]);

  useEffect(() => {
    const now = new Date();
    setRuntime(now.toLocaleString("en-GB", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    }));
  }, []);

  useEffect(() => {
    if (!clientId || !token) return;

    API.get("/guests/all", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setGuests(res.data))
      .catch(err => console.error("❌ Failed to load guests", err));
  }, []);

  useEffect(() => {
    if (selectedNic && clientId) {
      API.get(`/guests/search/${selectedNic}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => setGuest(res.data))
        .catch(err => console.error("❌ Guest fetch error", err));

      API.get(`/bookings/by_nic/${selectedNic}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => {
          const filtered = res.data.filter(b => b.actual_checkin_time || b.actual_checkout_time || b.room_type || b.room_rate || b.companions);
          setBookings(filtered);
        })
        .catch(err => console.error("❌ Booking fetch error", err));
    }
  }, [selectedNic]);

  function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <label>Select Guest:</label>
      <select onChange={(e) => setSelectedNic(e.target.value)} value={selectedNic}>
        <option value="">-- Select Guest --</option>
        {guests.map((b) => (
          <option key={b.nic_passport_number} value={b.nic_passport_number}>
            {b.nic_passport_number} - {b.guest_name}
          </option>
        ))}
      </select>

      {selectedNic && (
      <div id="report-section" style={{ marginTop: "30px", border: "1px solid #ccc", padding: "20px" }}>
          {/* ✅ HEADER WITH LOGO AND NAME */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>{runtime}</div>

        {/* ✅ UPDATED: Logo and name side-by-side */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1 }}>
          {companyLogo && (
            <img
              src={companyLogo}
              alt="Company Logo"
              style={{ maxHeight: "50px", marginRight: "12px" }} // ✅ CHANGED: marginRight instead of marginBottom
            />
          )}
          <div style={{ fontWeight: "bold", fontSize: "18px" }}>
            {companyName}
          </div>
        </div>

        <div style={{ width: "100px" }}></div>
      </div>

            

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", rowGap: "8px", marginBottom: "20px" }}>
            <div><strong>NIC:</strong> {guest.nic_passport_number}</div>
            <div><strong>Name:</strong> {guest.name}</div>
            <div><strong>Contact:</strong> {guest.contact_number}</div>
            <div><strong>Email:</strong> {guest.email}</div>
            <div><strong>Nationality:</strong> {guest.nationality}</div>
            <div><strong>Emergency Contact:</strong> {guest.emergency_contact}</div>
            <div><strong>Address:</strong> {guest.address}</div>
          </div>

          {/* ✅ UPDATED Booking Header */}
          <div style={{ display: "flex", fontWeight: "bold", borderBottom: "1px solid #000", paddingBottom: "5px" }}>
            <div style={{ flex: 1 }}>Actual Check-in</div>
            <div style={{ flex: 1 }}>Actual Check-out</div>
            <div style={{ flex: 1 }}>Room</div>
            <div style={{ flex: 1 }}>Type</div>
            <div style={{ flex: 1 }}>Rate</div>
            <div style={{ flex: 1 }}>Companions</div>
          </div>

          {/* ✅ UPDATED Booking Rows */}
          {bookings.map((b, index) => (
            <div key={index} style={{ display: "flex", paddingTop: "5px", borderBottom: "1px dotted #aaa" }}>
              <div style={{ flex: 1 }}>{formatDate(b.actual_checkin_time)}</div>
              <div style={{ flex: 1 }}>{formatDate(b.actual_checkout_time)}</div>
              <div style={{ flex: 1 }}>{b.room_number}</div>
              <div style={{ flex: 1 }}>{b.room_type}</div>
              <div style={{ flex: 1 }}>Rs. {b.room_rate?.toLocaleString()}</div>
              <div style={{ flex: 1 }}>{b.companions}</div>
            </div>
          ))}

          <div style={{ marginTop: "40px", textAlign: "center", fontStyle: "italic" }}>
            Page {currentPage} of {totalPages}
            <br />
            Developed by Aarkay's Solutions | © {new Date().getFullYear()} SmartHost
          </div>
        </div>
      )}

      <button onClick={() => window.print()} style={{ marginTop: "20px" }}>
        🖨️ Print / Export PDF
      </button>
    </div>
  );
};

export default GuestStayReport;
