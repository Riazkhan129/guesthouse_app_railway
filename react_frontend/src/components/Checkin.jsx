import React, { useEffect, useState, useContext } from "react";
// import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import API from "../api"; // ✅ ADDED: Centralized Axios instance
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function Checkin() {
  const { token } = useContext(AuthContext);

  const [bookings, setBookings] = useState([]);
  const [vacantRooms, setVacantRooms] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState("");
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState("");
  const [checkoutDate, setCheckoutDate] = useState(() => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    return tomorrow;
  });

const formatToDisplayDate = (isoDateStr) => {
  if (!isoDateStr) return "";
  const date = new Date(isoDateStr);
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }); // e.g. "15 Aug 2025"
};


const formatDateTime = () => {
  const now = new Date();
  const options = {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  };
  return now.toLocaleString("en-GB", options).replace(",", " -");
};

const [actualCheckinDate, setActualCheckinDate] = useState(formatDateTime);
const [advancePayment, setAdvancePayment] = useState("");
const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    fetchTodayBookings();
    fetchVacantRooms();
  }, []);

  const fetchTodayBookings = async () => {
    try {
      const res = await API.get("/bookings/today", {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      if (res.status === 200) setBookings(res.data);
    } catch (err) {
      console.error("Error fetching today's bookings", err);
      setStatusMessage("❌ Failed to load bookings.");
    }
  };

  const fetchVacantRooms = async () => {
    try {
      const res = await API.get("/rooms/vacant", {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      if (res.status === 200) setVacantRooms(res.data);
    } catch (err) {
      console.error("Error fetching vacant rooms", err);
      setStatusMessage("❌ Failed to load rooms.");
    }
  };

  const handleBookingSelect = (bookingId) => {
    const booking = bookings.find((b) => b.booking_id === parseInt(bookingId));
    setSelectedBookingId(bookingId);
    setSelectedBooking(booking);
    setStatusMessage(""); // clear old messages
  };

  const handleCheckin = async () => {
    if (!selectedBooking || !selectedRoom || !checkoutDate) {
      setStatusMessage("⚠️ Please fill all fields before checking in.");
      return;
    }

    const now = new Date();
    const actualCheckinTime = now.toISOString().slice(0, 19).replace("T", " ");

    const payload = {
      room_number: selectedRoom,
      checkout_date: checkoutDate,
      actual_checkin_time: actualCheckinTime,
      advance_payment: parseFloat(advancePayment) || 0,
      status: "checked_in"
    };

    try {
      const res = await API.put(
        `/checkin_checkout/checkin/${selectedBooking.booking_id}`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } } // ✅ CHANGED
      );
      if (res.status === 200) {
        alert("✅ Guest checked in successfully.");

        // Reset form
        setSelectedBookingId("");
        setSelectedBooking(null);
        setSelectedRoom("");
        setCheckoutDate(new Date().toISOString().split("T")[0]);
        setActualCheckinDate(new Date().toISOString().split("T")[0]);
        setAdvancePayment("");

        // Refresh data
        fetchTodayBookings();
        fetchVacantRooms();
      } else {
        setStatusMessage("❌ Failed to check-in.");
      }
    } catch (err) {
      console.error("Check-in error", err);
      setStatusMessage("❌ Error occurred during check-in.");
    }
  };

  function formatDateInput(value) {
  // Remove non-alphanumeric characters
  const cleaned = value.replace(/[^0-9a-zA-Z]/gi, '').toUpperCase();

  // Extract parts
  const day = cleaned.slice(0, 2);
  const month = cleaned.slice(2, 5);
  const year = cleaned.slice(5, 9);

  return `${day} ${month} ${year}`.trim();
}

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ fontSize: "22px", fontWeight: "bold", marginBottom: "16px" }}>
        📥 Guest Check-In
      </h2>

      {/* Booking Selection */}
      <div style={{ marginBottom: "16px" }}>
        <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>
          Select Booking:
        </label>
        <select
          value={selectedBookingId}
          onChange={(e) => handleBookingSelect(e.target.value)}
          style={{ padding: "8px", width: "100%", maxWidth: "600px" }}
        >
          <option value="">-- Choose booking for check-in --</option>
          {bookings.map((b) => (
            <option key={b.booking_id} value={b.booking_id}>
              {b.nic_passport_number} - {b.guest_name} ({b.checkin_date} to {b.checkout_date})
            </option>
          ))}
        </select>
      </div>

      {/* Booking Info */}
      {selectedBooking && (
        <div
          style={{
            background: "#f9f9f9",
            padding: "15px",
            borderRadius: "6px",
            marginBottom: "20px",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            columnGap: "20px",
            rowGap: "10px",
            border: "1px solid #ccc"
          }}
        >
          <p><strong>NIC:</strong> {selectedBooking.nic_passport_number}</p>
          <p><strong>Guest Name:</strong> {selectedBooking.guest_name}</p>
          <p><strong>Check-in:</strong> {formatToDisplayDate(selectedBooking.checkin_date)}</p>
          <p><strong>Planned Check-out:</strong> {formatToDisplayDate(selectedBooking.checkout_date)}</p>
        </div>
      )}

      {/* Form Inputs */}
      {selectedBooking && (
        <>
          <div style={{ display: "flex", gap: "50px", marginBottom: "15px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontWeight: "bold", marginBottom: "5px", display: "block" }}>
                Assign Room:
              </label>
              <select
                value={selectedRoom}
                onChange={(e) => setSelectedRoom(e.target.value)}
                style={{ padding: "8px", width: "100%" }}
              >
                <option value="">-- Select vacant room --</option>
                {vacantRooms.map((room) => (
                  <option key={room.room_number} value={room.room_number}>
                    Room {room.room_number} ({room.type})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ fontWeight: "bold", marginBottom: "5px", display: "block" }}>
                Actual Check-in Date:
              </label>
              <input
                type="text"
                value={actualCheckinDate}
                readOnly
                // onChange={(e) => setActualCheckinDate(e.target.value)}
                 style={{ padding: "8px", width: "100%", backgroundColor: "#f0f0f0", cursor: "not-allowed" }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "50px", marginBottom: "15px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontWeight: "bold", marginBottom: "5px", display: "block" }}>
                Planned Check-out Date:
              </label>
                <DatePicker
                    selected={checkoutDate}
                    onChange={(date) => setCheckoutDate(date)}
                    dateFormat="dd MMM yyyy"
                    minDate={new Date(new Date().getTime() + 24 * 60 * 60 * 1000)} // Prevent same-day checkout
                    className="react-datepicker-input"
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                  />

              </div>

            <div style={{ flex: 1 }}>
              <label style={{ fontWeight: "bold", marginBottom: "5px", display: "block" }}>
                Advance Payment (Rs.):
              </label>
              <input
                type="number"
                value={advancePayment}
                onChange={(e) => setAdvancePayment(e.target.value)}
                style={{ padding: "8px", width: "100%" }}
              />
            </div>
          </div>

          {/* Submit */}
          <button
            onClick={handleCheckin}
            style={{
              backgroundColor: "green",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            ✅ Confirm Check-in
          </button>

          {/* Status message */}
          {statusMessage && (
            <div style={{ marginTop: "15px", fontWeight: "bold", color: "#0055aa" }}>
              {statusMessage}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Checkin;
