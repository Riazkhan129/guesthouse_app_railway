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
  const [modeOfPayment, setModeOfPayment] = useState("");
  const [profession, setProfession] = useState("");
  const [purposeOfVisit, setPurposeOfVisit] = useState("");

  
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
const [roomRate, setRoomRate] = useState(""); // ✅ ADDED
const [companions, setCompanions] = useState("0"); // ✅ ADDED
const [roomType, setRoomType] = useState(""); // ✅ ADDED


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
      status: "checked_in",
      room_rate: parseFloat(roomRate) || 0,       // ✅ ADDED
      companions: companions.trim(),                // ✅ ADDED
      room_type: roomType,                         // ✅ ADDED
      mode_of_payment: modeOfPayment.trim(),       // ✅ NEW
      profession: profession.trim(),               // ✅ NEW
      purpose_of_visit: purposeOfVisit.trim()      // ✅ NEW
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
        setRoomRate("");       // ✅ ADDED
        setCompanions("");      // ✅ ADDED
        setRoomType("");       // ✅ ADDED


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
        <>
        <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
          <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "8px" }}>
            <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>NIC:</label>
            <div>{selectedBooking.nic_passport_number}</div>
          </div>

          <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "8px" }}>
            <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>Guest Name:</label>
            <div>{selectedBooking.guest_name}</div>
          </div>

          {selectedBooking.corporate_name && (
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "8px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>Company:</label>
              <div>{selectedBooking.corporate_name}</div>
            </div>
          )}
        </div>

      
          
          {/* 🔧 ROW 1: Room No + Room Type */}
          <div style={{ display: "flex", gap: "50px", marginBottom: "15px" }}>
            {/* Assign Room */}
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Assign Room:
              </label>
              <select
                value={selectedRoom}
                onChange={(e) => {
                  const roomNumber = e.target.value;
                  setSelectedRoom(roomNumber);
                  const selected = vacantRooms.find((r) => r.room_number === roomNumber);    
                  if (selected) {
                    setRoomRate(selected.price || "");
                  }
                }}                 
                style={{ width: "200px", padding: "8px" }}
              >
                <option value="">-- Select vacant room --</option>
                {vacantRooms.map((room) => (
                  <option key={room.room_number} value={room.room_number}>
                    Room {room.room_number} ({room.type})
                  </option>
                ))}
                </select>
              </div>
            

            {/* Room Type */}
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Room Type:
              </label>
              <select
                value={roomType}
                onChange={(e) => setRoomType(e.target.value)}
                style={{ width: "200px", padding: "8px", }}
              >
                <option value="">-- Select Room Type --</option>
                <option value="AC">AC</option>
                <option value="Non-AC">Non-AC</option>
              </select> 
              </div>
            </div>

            {/* 🔧 ROW 2: Room Rate + Companion */}
            <div style={{ display: "flex", gap: "50px", marginBottom: "15px" }}>
              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Room Rate (Rs.):
              </label>
              <input
                type="number"
                value={roomRate}
                onChange={(e) => setRoomRate(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>
                
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Companions :
              </label>
              <input
                type="number"
                value={companions}
                onChange={(e) => setCompanions(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>
          </div>

          {/* 🔧 ROW 3: Mode of Payment + Profession */}
          <div style={{ display: "flex", gap: "50px", marginBottom: "15px" }}>
            {/* Mode of Payment */}
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Mode of Payment:
              </label>
              <input
                type="text"
                value={modeOfPayment}
                onChange={(e) => setModeOfPayment(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>

            {/* Profession */}
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Profession:
              </label>
              <input
                type="text"
                value={profession}
                onChange={(e) => setProfession(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>
            </div>

            {/* Row 4 Purpose of Visit + checkin date*/}
            <div style={{  display: "flex", gap: "50px", marginBottom: "15px" }}>
              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}> 
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Purpose of Visit:
              </label>
              <input
                type="text"
                value={purposeOfVisit}
                onChange={(e) => setPurposeOfVisit(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>

              {/* Check-in Date */}
              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
                <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Check-in :
              </label>
              <input
                type="text"
                value={actualCheckinDate}
                readOnly
                style={{ padding: "8px", width: "200px", backgroundColor: "#f0f0f0", cursor: "not-allowed" }}
                // onChange={(e) => setActualCheckinDate(e.target.value)}
                // style={{ padding: "8px", width: "100%", backgroundColor: "#f0f0f0", cursor: "not-allowed" }}
              />
            </div>
            </div>
          
            {/* Row 5 Planned Check-out + Advance*/}
            <div style={{ display: "flex", gap: "50px", marginBottom: "15px"}}>
              {/* ✅ Planned Check-out */}
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}> {/* ✅ Wrapped in flex container */}
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Planned Check-out:
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
                    style={{ width: "200px", padding: "8px" }}
                  />
              </div>

              {/* Advance Payment */}
              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
              <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Advance (Rs.):
              </label>
              <input
                type="number"
                value={advancePayment}
                onChange={(e) => setAdvancePayment(e.target.value)}
                style={{ width: "200px", padding: "8px" }}
              />
            </div>
          </div>

          {/* Submit */}
          <div style={{ textAlign: "center", marginTop: "20px" }}>
          <button
            onClick={handleCheckin}
            style={{
              backgroundColor: "green",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "16px"
            }}
          >
            ✅ Confirm Check-in
          </button>
        </div>

          {/* Status message */}
          {statusMessage && (
            <div style={{ marginTop: "15px", fontWeight: "bold", color: "#0055aa" }}>
              {statusMessage}
            </div>
          )}
      </>
      )}
        </div> 
      )};  

export default Checkin;
