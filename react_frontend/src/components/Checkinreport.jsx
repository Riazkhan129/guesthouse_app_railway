import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import "../print.css";
import { AuthContext } from "../context/AuthContext";

const Checkinreport = () => {
  const [bookings, setBookings] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState("");
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [guest, setGuest] = useState(null);
  const [companyLogo, setCompanyLogo] = useState([]);
  const [companyName, setCompanyName] = useState("Loading...");
  const { token, clientId } = useContext(AuthContext);

  useEffect(() => {
    if (!clientId || !token) return;

    API.get(`/meta/guesthouse/${clientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => {
        setCompanyLogo(res.data?.logo || null);
        setCompanyName(res.data?.guesthouse_name || "Unknown Company");
      })
      .catch(() => setCompanyName("Unknown Company"));
  }, [clientId, token]);

  useEffect(() => {
    const fetchCheckedInBookings = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await API.get("/checkin_checkout/checkedin", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.status === 200) {
          setBookings(res.data);
        }
      } catch (err) {
        console.error("❌ Failed to load checked-in bookings.", err);
      }
    };
    fetchCheckedInBookings();
  }, []);

  const handleBookingSelect = async (bookingId) => {
    setSelectedBookingId(bookingId);
    const booking = bookings.find((b) => b.booking_id === parseInt(bookingId));
    if (!booking) {
      setSelectedBooking(null);
      setGuest(null);
      return;
    }

    setSelectedBooking(booking);
    try {
      const token = localStorage.getItem("token");
      const guestRes = await API.get(`/checkin_checkout/guest_name/${booking.nic_passport_number}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (guestRes.status === 200) {
        setGuest(guestRes.data);
      } else {
        setGuest(null);
      }
    } catch (err) {
      console.error("❌ Failed to fetch guest info.", err);
      setGuest(null);
    }
  };

  const printReport = () => {
    const content = document.getElementById("print-section").innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Print Check-In Report</title>
          <style>
            body { font-family: Arial; padding: 20px; }
            .row { display: flex; justify-content: space-between; margin-bottom: 10px; }
            .label { font-weight: bold; width: 150px; }
          </style>
        </head>
        <body>
          ${content}
          <script>
            window.onload = function() {
              window.print();
              window.onafterprint = function () { window.close(); }
            }
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div style={{ padding: "20px" }}>
      {/* Booking dropdown */}
      {bookings.length > 0 ? (
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>
            Select a Booking to view report:
          </label>
          <select
            value={selectedBookingId}
            onChange={(e) => handleBookingSelect(e.target.value)}
            style={{ padding: "8px", width: "100%", maxWidth: "400px" }}
          >
            <option value="">-- Select Booking --</option>
            {bookings.map((b) => (
              <option key={b.booking_id} value={b.booking_id}>
                Booking #{b.booking_id} | {b.nic_passport_number} | Room {b.room_number}
              </option>
            ))}
          </select>
        </div>
      ) : (
        <p>No guests currently checked in.</p>
      )}

      {/* Printable report */}
      {selectedBooking && guest && (
        <div id="print-section" style={{ border: "1px solid #ccc", padding: "30px", maxWidth: "800px", margin: "auto" }}>
         <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "30px" }}>
          {companyLogo && (
            <img
              src={companyLogo}
              alt="Company Logo"
              style={{ maxHeight: "50px", marginRight: "12px" }} // ✅ Logo appears here
            />
          )}
          <h2 style={{ margin: 0, fontSize: "1.5rem" }}> {companyName}</h2> 
        </div>

          <h3 style={{ textAlign: "center", marginBottom: "30px" }}>📝 Guest Check-In Report</h3>

          {[
            { label1: "Guest Name:", value1: guest.name, label2: "NIC/Passport:", value2: guest.nic_passport_number },
            { label1: "Room #:", value1: selectedBooking.room_number, label2: "Room Rate:", value2: `Rs. ${selectedBooking.room_rate}` },
            { label1: "Advance Payment:", value1: `Rs. ${selectedBooking.advance_payment}`, label2: "Companions:", value2: selectedBooking.companions },
            { label1: "Nationality:", value1: guest.nationality, label2: "Email:", value2: guest.email },
            { label1: "Contact No:", value1: guest.contact, label2: "Emergency Contact:", value2: guest.emergency_contact },
            { label1: "Company Name:", value1: guest.corporate_name, label2: "Profession:", value2: selectedBooking.profession },
            { label1: "Purpose of Visit:", value1: selectedBooking.purpose_of_visit, label2: "Mode of Payment:", value2: selectedBooking.mode_of_payment },
            { label1: "Check-In Date/Time:", value1: selectedBooking.actual_checkin_time, label2: "Planned Check-Out:", value2: selectedBooking.planned_checkout_date },
          ].map((row, idx) => (
            <div key={idx} style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
              <div style={{ display: "flex", width: "45%" }}>
                <div style={{ width: "150px", fontWeight: "bold" }}>{row.label1}</div>
                <div>{row.value1}</div>
              </div>
              <div style={{ display: "flex", width: "45%" }}>
                <div style={{ width: "150px", fontWeight: "bold" }}>{row.label2}</div>
                <div>{row.value2}</div>
              </div>
            </div>
          ))}

          {/* Signatures */}
          <div style={{ height: "40px" }}></div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "40px" }}>
            <div><strong>Manager</strong> ____________________________</div>
            <div><strong>Guest</strong> ____________________________</div>
          </div>
        </div>
      )}

      {/* Print button */}
      {selectedBooking && guest && (
        <div style={{ textAlign: "center", marginTop: "20px" }}>
          <button
            onClick={printReport}
            style={{
              padding: "10px 20px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            🖨️ Print Check-In Report
          </button>
        </div>
      )}
    </div>
  );
};

export default Checkinreport;
