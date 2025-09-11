import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000"; // Replace with your actual backend
const headers = { Authorization: "Bearer your_token_here" }; // Add auth if needed

const GuestReport = () => {
  const [guests, setGuests] = useState([]);
  const [selectedNic, setSelectedNic] = useState("");
  const [guest, setGuest] = useState({});
  const [bookings, setBookings] = useState([]);
  const [runtime, setRuntime] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(bookings.length / 15); // assuming 5 bookings per page

  
  function formatDate(dateString) {
    if (!dateString) return ""; // Handle null or undefined
    const date = new Date(dateString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  function formatDateOnly(dateString) {
    if (!dateString) return ""; // Handle null or undefined
    const date = new Date(dateString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }
  useEffect(() => {
    const now = new Date();
    setRuntime(now.toLocaleString("en-GB", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    }));
  }, []);

  // Load NICs from bookings with actual_checkin_time
  useEffect(() => {
    axios.get(`${API_URL}/guests/all`, { headers })

      .then(res => setGuests(res.data))
      .catch(err => console.error("❌ Failed to load guests", err));
  }, []);

  // Load guest and all bookings
  useEffect(() => {
    if (selectedNic) {
      axios.get(`${API_URL}/guests/search/${selectedNic}`, { headers })
        .then(res => setGuest(res.data))
        .catch(err => console.error("❌ Guest fetch error", err));

      axios.get(`${API_URL}/bookings/by_nic/${selectedNic}`, { headers })
        .then(res => {
          console.log("📦 Raw booking data:", res.data);
          const filtered = res.data.filter(b => b.actual_checkin_time);
          console.log("✅ Filtered bookings (with check-in):", filtered);
          setBookings(filtered);
        })
        .catch(err => console.error("❌ Booking fetch error", err));
    }
  }, [selectedNic]);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      {/* Guest Selection */}
      <label>Select Guest:</label>
      <select onChange={(e) => setSelectedNic(e.target.value)} value={selectedNic}>
        <option value="">-- Select Guest --</option>
        {guests.map((b) => (
          <option key={b.nic_passport_number} value={b.nic_passport_number}>
            {b.nic_passport_number} - {b.guest_name}
          </option>
        ))}
      </select>

      {/* Report Layout */}
      {selectedNic && (
        <div id="report-section" style={{ marginTop: "30px", border: "1px solid #ccc", padding: "20px" }}>
          {/* Top Line */}
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
            <div>{runtime}</div>
            <div style={{ textAlign: "center", flex: 1, fontWeight: "bold", fontSize: "18px" }}>
              🏨 Nursery Guest House
            </div>
            <div style={{ width: "100px" }}></div>
          </div>

          {/* Guest Identity */}
         
          {/* Guest Details */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", rowGap: "8px", marginBottom: "20px" }}>
            <div><strong>NIC:</strong> {guest.nic_passport_number}</div>
            <div><strong>Name:</strong> {guest.name}</div>
            <div><strong>Contact:</strong> {guest.contact_number}</div>
            <div><strong>Email:</strong> {guest.email}</div>
            <div><strong>Nationality:</strong> {guest.nationality}</div>
            <div><strong>Emergency Contact:</strong> {guest.emergency_contact}</div>
            <div><strong>Address:</strong> {guest.address}</div>
          </div>

          {/* Booking Header */}
          <div style={{ display: "flex", fontWeight: "bold", borderBottom: "1px solid #000", paddingBottom: "5px" }}>
            <div style={{ flex: 1 }}>Planned Check-in</div>
            <div style={{ flex: 1 }}>Planned Check-out</div>            
            <div style={{ flex: 1 }}>Actual Check-in</div>
            <div style={{ flex: 1 }}>Actual Check-out</div>
            <div style={{ flex: 1 }}>Room</div>
          </div>
        {/* Booking Rows */}
        {bookings.map((b, index) => (
          <div key={index} style={{ display: "flex", paddingTop: "5px", borderBottom: "1px dotted #aaa" }}>
            <div style={{ flex: 1 }}>{formatDateOnly(b.checkin_date)}</div>
            <div style={{ flex: 1 }}>{formatDateOnly(b.checkout_date)}</div>
            <div style={{ flex: 1 }}>{formatDate(b.actual_checkin_time)}</div>
            <div style={{ flex: 1 }}>{formatDate(b.actual_checkout_date)}</div>
            <div style={{ flex: 1 }}>{b.room_number}</div>
          </div>
        ))}

        {/* Footer */}
        <div style={{ marginTop: "40px", textAlign: "center", fontStyle: "italic" }}>
          Page {currentPage} of {totalPages}
          <br />
          Developed by Aarkay's Solutions | © {new Date().getFullYear()} LodgeControl
        </div>
      </div>
      )}

      {/* Print Button */}
      <button onClick={() => window.print()} style={{ marginTop: "20px" }}>
        🖨️ Print / Export PDF
      </button>
    </div>
  );
};

export default GuestReport;
