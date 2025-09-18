import { useEffect, useState, useContext } from "react";
// import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import Billing from "./Billing";
import API from "../api"; // ✅ ADDED: Centralized Axios instance

function Checkout() {
  const { token } = useContext(AuthContext);

  const [bookings, setBookings] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState("");
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [guest, setGuest] = useState(null);
  const [roomPrice, setRoomPrice] = useState(0);
  const [totalNights, setTotalNights] = useState(1);
  const [statusMessage, setStatusMessage] = useState("");

  const formatDateTime = (isoDateStr) => {
  if (!isoDateStr) return "";
  const date = new Date(isoDateStr);
  const datePart = date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }); // "13 Aug 2025"

  const timePart = date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }); // "15:50"

  return `${datePart} - ${timePart}`;
};


  // Load checked-in bookings on component mount
  useEffect(() => {
    fetchCheckedInBookings();
  }, []);

  const fetchCheckedInBookings = async () => {
    try {
      const res = await API.get("/checkin_checkout/checkedin", {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      // setCheckedInBookings(res.data);
      if (res.status === 200) {
        setBookings(res.data);
        setStatusMessage("");
      }
    } catch (err) {
      console.error("❌ Failed to load checked-in bookings.", err);
      setStatusMessage("❌ Error loading checked-in guests.");
    }
  };

  const handleBookingSelect = async (bookingId) => {
    setSelectedBookingId(bookingId);
    const booking = bookings.find((b) => b.booking_id === parseInt(bookingId));
    if (!booking) {
      setSelectedBooking(null);
      setGuest(null);
      return;
    }

    setSelectedBooking(booking);
    const nic = booking.nic_passport_number;
    const roomNumber = booking.room_number;

    try {
      console.log("IN CHECKOUT - before getting GUEST_NAME");
      const guestRes = await API.get(`/checkin_checkout/guest_name/${nic}`, {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      setGuest(guestRes.status === 200 ? guestRes.data : { name: "Unknown" });
      console.log("IN CHECKOUT - before getting ROOMNUMBER");
      const roomRes = await API.get(`/checkin_checkout/${roomNumber}`, {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      setRoomPrice(roomRes.status === 200 ? roomRes.data.price : 0);

      const checkinDate = new Date(booking.checkin_date);
      const today = new Date();
      const diffTime = Math.abs(today - checkinDate);
      const nights = Math.max(Math.ceil(diffTime / (1000 * 60 * 60 * 24)), 1);
      setTotalNights(nights);
    } catch (err) {
      console.error("❌ Error during checkout flow:", err);
      setStatusMessage("❌ Failed to load guest or room info.");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "10px" }}>
        🏁 Guest Checkout
      </h2>

      {statusMessage && (
        <div style={{ marginBottom: "10px", color: "red", fontWeight: "bold" }}>
          {statusMessage}
        </div>
      )}

      {/* Select guest dropdown */}
      {bookings.length > 0 ? (
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>
            Select a Guest to check out:
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

      {/* Show selected guest and booking info */}
      {selectedBooking && guest && (
        <div
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            marginTop: "20px",
            borderRadius: "5px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h4 style={{ marginBottom: "10px" }}>Guest & Booking Details</h4>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          <p style={{ margin: "4px 0" }}><strong>NIC:</strong> {selectedBooking.nic_passport_number}</p>
          <p style={{ margin: "4px 0" }}><strong>Guest Name:</strong> {guest.name}</p>

          <p style={{ margin: "4px 0" }}><strong>Room Number:</strong> {selectedBooking.room_number}</p>
          <p style={{ margin: "4px 0" }}><strong>Room Price:</strong> Rs. {roomPrice.toLocaleString()}</p>

          <p style={{ margin: "4px 0" }}>
            <strong>Check-in:</strong> {formatDateTime(selectedBooking.actual_checkin_time)}
          </p>

          <p style={{ margin: "4px 0" }}><strong>Advance Paid:</strong> Rs. {(selectedBooking.advance_payment ??0).toLocaleString()}</p>

          <p style={{ margin: "4px 0" }}><strong>Total Nights:</strong> {totalNights}</p>
        </div>



          {/* Billing component */}
          <div style={{ marginTop: "20px" }}>
            <Billing
              selectedBooking={selectedBooking}
              guest={guest}
              roomPrice={roomPrice}
              totalNights={totalNights}
              // 🔧 UPDATED: Add callback to reset view after checkout
              onCheckoutComplete={() => {
                setSelectedBooking(null); // 🔧 Clear booking
                setGuest(null);           // 🔧 Clear guest
                setSelectedBookingId(""); // 🔧 Reset dropdown
                fetchCheckedInBookings();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default Checkout;
