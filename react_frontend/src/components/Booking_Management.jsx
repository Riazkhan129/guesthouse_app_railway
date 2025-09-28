import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { format } from "date-fns";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import API from "../api"; // ✅ ADDED: Centralized Axios instance
import { AuthContext } from "../context/AuthContext"; // ✅ ADDED: For token

function BookingManagement() {
  const { token } = useContext(AuthContext);
  const [action, setAction] = useState("Create Booking");
  const [guests, setGuests] = useState([]);
  const [selectedGuest, setSelectedGuest] = useState(null);
  const [checkinDate, setCheckinDate] = useState(() =>
    new Date().toISOString().split("T")[0]
  );
  const [checkoutDate, setCheckoutDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
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

  const [availability, setAvailability] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState(null);
  const [bookingCreated, setBookingCreated] = useState(false);
  const [guestNames, setGuestNames] = useState({}); // 📦 {nic: name}
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [bookingDate, setBookingDate] = useState(() =>
    new Date().toISOString().split("T")[0]
  ); // ✅ Clean and correct

// ✅ Automatically check availability on page load
  useEffect(() => {
    if (bookingDate) {
      console.log("handleCheckAvailability from useEffect:", bookingDate);
      handleCheckAvailability(bookingDate);
    }
  }, [bookingDate]);

useEffect(() => {
  const fetchGuestNames = async () => {
    const nicList = bookings.map(b => b.nic_passport_number);
    const uniqueNICs = [...new Set(nicList)];
    const nameMap = {};
    for (const nic of uniqueNICs) {
      try {
        const res = await API.get(`/guests/search/${nic}`);
        nameMap[nic] = res.data.name; // ⬅️ Adjust if the field is different
      } catch {
        nameMap[nic] = "Unknown Guest";
      }
    }
    setGuestNames(nameMap); // ✅ store names
  };

  if (bookings.length > 0) {
    fetchGuestNames();
  }
}, [bookings]);


  useEffect(() => {
    if (action === "Create Booking") {
      API.get("/guests/all", { headers: { Authorization: `Bearer ${token}` } }) // 🔧 CHANGED
        .then(res => setGuests(res.data))
        .catch(() => alert("❌ Failed to load guest list."));
    }
    if (["View All Bookings", "Cancel Booking", "Upcoming Booking"].includes(action)) {
      const endpoint = action === "Upcoming Booking" ? "upcoming" : "";
      API.get(`/bookings/${endpoint}`, { headers: { Authorization: `Bearer ${token}` } }) // 🔧 CHANGED
        .then(res => setBookings(res.data))
        .catch(() => alert("❌ Failed to load bookings."));
    }
  }, [action, token]);

  const fetchBookings = () => {
  API.get("/bookings", { headers: { Authorization: `Bearer ${token}` } }) // 🔧 CHANGED
    .then((res) => {setBookings(res.data) // 🎯 Update list with fresh data
    })
    .catch((err) => {console.error("Failed to fetch bookings:", err);
  });
};
  const handleCheckAvailability = (date) => {
  API.get("/bookings/total", {params: { checkin_date: date } }) 
    .then((res) => {setAvailability(res.data)
    })
    .catch(() => alert("❌ Failed to check room availability."));
  };

  const handleCreateBooking = () => {
    if (!selectedGuest) return;
    const payload = {
      nic_passport_number: selectedGuest.nic_passport_number,
      room_number: 0,
      checkin_date: checkinDate,
      checkout_date: checkoutDate,
      status: "booked",
      notes: "notes",
      advance_payment: 0,
      total_payment: 0,
      booked_rooms: availability?.booked_rooms,
      total_rooms: availability?.total_rooms,
    };
    
    API.post("/bookings/", payload) // 🔧 CHANGED
    .then(() => {
      alert("✅ Booking created successfully!");
      setBookingCreated(true); 
      console.log("📅 handleCheckAvailability from handlecreatebooking:", checkinDate);
      handleCheckAvailability(checkinDate);
    })
    .catch((err) => {
      console.error("❌ Booking failed:", err.response?.data || err.message);
      alert("❌ Failed to create booking.");
    });
  };

  const handleCancelBooking = (bookingId, roomNumber) => {
    API.put(`/bookings/cancel/${bookingId}`, { room_number: roomNumber }, { headers: { Authorization: `Bearer ${token}` } })
    .then(() => {
      alert("✅ Booking cancelled.");
      setSelectedBookingId("");
      setSelectedBooking(null);
      fetchBookings();
    })
    .catch((err) => {
      alert(`❌ Failed to cancel: ${err.response?.data?.detail || err.message}`);
    });
};


  return (
    <div style={{ padding: "20px" }}>
      <h2>📋 Booking Management</h2>

      <div style={{ marginBottom: "20px", display: "flex", gap: "20px", flexWrap: "nowrap" }}>
      {["Create Booking", "Cancel Booking", "Upcoming Booking", "View All Bookings"].map((opt) => (
        <label key={opt} style={{ display: "flex", alignItems: "center", gap: "6px", whiteSpace: "nowrap" }}>
          <input
            type="radio"
            name="action"
            value={opt}
            checked={action === opt}
            onChange={(e) => setAction(e.target.value)}
          />
          <span>{opt}</span>
        </label>
      ))}
      </div>

      {/* Create Booking */}
      {action === "Create Booking" && (
        <div>
          <h3>🆕 Create New Booking</h3>
          <select onChange={(e) => { 
            const guest = guests.find(g => `${g.nic_passport_number} - ${g.name}` === e.target.value);
            setSelectedGuest(guest);
            setBookingCreated(false);           
          }}>
            <option>Select Guest</option>
            {guests.map((g) => (
              <option key={g.nic_passport_number}>{`${g.nic_passport_number} - ${g.name}`}</option>
            ))}
          </select>

          {selectedGuest && !bookingCreated && (
            <div style={{ marginTop: 10 }}>
              {/* 🔧 FIXED: Removed flex-wrap layout that was interfering with centering */}
              <div style={{ display: "flex", gap: "20px" }}>
                {/* Column 1 */}
                <div style={{ flex: "1 1 45%" }}>
                <p><strong>NIC:</strong> {selectedGuest.nic_passport_number}</p>
                <p><strong>Name:</strong> {selectedGuest.name}</p>
            </div>

            {/* Column 2 */}
            <div style={{ flex: "1 1 45%" }}>
              <p><strong>Guest Type:</strong> {selectedGuest.guest_type || 'N/A'}</p>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
                <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                Check-in Date:
              </label>
              <DatePicker
                selected={checkinDate} // 🔧 Pass Date object
                onChange={(date) => {
                  if (!date) return;
                  const dateOnly = date.toISOString().split("T")[0];
                  setCheckinDate(dateOnly); 
                  const nextDay = new Date(date);
                  nextDay.setDate(date.getDate() + 1);
                  setCheckoutDate(nextDay);
                  console.log("handleCheckAvailability from createbooking:", dateOnly);
                  handleCheckAvailability(dateOnly); // 🔧 Pass raw date to your logic
                }}
                dateFormat="dd MMM yyyy" // 🔧 Format as "12 Aug 2025"
                placeholderText="Select check-in date"
                className="react-datepicker-input"
                showMonthDropdown
                showYearDropdown
                dropdownMode="select"
                minDate={new Date()} // 🔧 Prevent dates before today
              />
              </div>
              {/* ✅ Availability Block — separated and centered */}
              {availability && (
                
                <div style={{ marginTop: 20 }}> 
                <div style={{ display: "flex", justifyContent: "flex-start", gap: "20px" }}>
              {/* <div
                   style={{                   
                    display: "flex",              
                    justifyContent: "flex-start",
                    alignItems: "left",        
                    gap: "40px",                 
                    backgroundColor: "#f9f9f9",  
                    padding: "10px 20px",
                    borderRadius: "6px",
                    
                    width: "100%",        
                    maxWidth: "100%"                
                  }}> */}
                
                  
                 <div style={{ textAlign: "left", flex: "1 1 30%" }}>
                  <p><strong>✅ Total:</strong> {availability.total_rooms}</p>
                </div>
                <div style={{ textAlign: "left",flex: "1 1 30%" }}>
                  <p><strong>📦 Booked:</strong> {availability.booked_rooms}</p>
                </div>
                <div style={{ textAlign: "left", flex: "1 1 30%" }}>
                  <p><strong>🟢 Available:</strong> {availability.available_rooms}</p>
                </div>
              </div>
               
            
              {availability?.available_rooms > 0 ? (
                <>
                  <label style={{ fontWeight: "bold", display: "block", marginBottom: "5px" }}>
                    Check-out Date:
                  </label>
                  <DatePicker
                    selected={checkoutDate}
                    onChange={(date) => setCheckoutDate(date)}
                    dateFormat="dd MMM yyyy"
                    placeholderText="Select check-out date"
                    className="react-datepicker-input"
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    minDate={checkinDate} 
                  />

                  <div style={{ textAlign: "center", marginTop: "20px" }}>
                    <button
                      onClick={handleCreateBooking}
                      style={{
                        padding: "10px 20px",
                        backgroundColor: "green",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "16px"
                      }}
                    >
                      ✅ Create Booking
                    </button>
                  </div>
                </>
              ) : (
                <p style={{ color: "red", fontWeight: "bold" }}>
                  All Rooms are Booked for this date {checkinDate}
                </p>
              )}
              </div>              
            )}
          </div>
        </div>    
    </div>
  )}
  </div>
)}

      {/* View All Bookings */}
      {action === "View All Bookings" && (
        <div>
          <h3>📖 All Bookings</h3>
          {bookings.map(b => (
            <div
              key={b.booking_id}
              style={{
                border: "1px solid #ccc",
                marginBottom: "10px",
                padding: "10px",
                display: "flex",
                flexWrap: "wrap",
                gap: "10px"
              }}
            >
              <div style={{ width: "48%" }}>
                <strong>NIC:</strong> {b.nic_passport_number}
              </div>
              <div style={{ width: "48%" }}>
                <strong>Guest:</strong> {guestNames[b.nic_passport_number] || b.nic_passport_number}
              </div>
              <div style={{ width: "48%" }}>
                <strong>Check-in:</strong> {formatToDisplayDate(b.checkin_date)}
              </div>
              <div style={{ width: "48%" }}>
                 <strong>Check-out:</strong> {formatToDisplayDate(b.checkout_date)}
              </div>
              <div style={{ width: "48%" }}>
                <strong>Status:</strong> {b.status}
              </div>
              {b.notes && (
                <div style={{ width: "48%" }}>
                  <strong>Notes:</strong> {b.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Cancel Booking */}
      {action === "Cancel Booking" && (
      <div>
        <h3>❌ Cancel Booking</h3>

        {/* Booking Selection Dropdown */}
        <select
          value={selectedBookingId}
          onChange={(e) => {
            const id = e.target.value;
            setSelectedBookingId(id);

            const booking = bookings.find(
              (b) => b.booking_id.toString() === id
            );
            setSelectedBooking(booking || null);
          }}
        >
          <option value="">Select Booking</option>
          {bookings.map((b) => (
            <option key={b.booking_id} value={b.booking_id}>
              {`Booking ID: ${b.booking_id} — ${b.nic_passport_number} — ${b.checkin_date}`}
            </option>
          ))}
        </select>

        {/* Booking Preview */}
        {selectedBooking && (
          <div className="booking-preview">
            <h4>Booking Preview</h4>
            <p>
              <strong>NIC/Passport:</strong> {selectedBooking.nic_passport_number}
            </p>
            <p>
              <strong>Guest:</strong>{" "}
              {guestNames[selectedBooking.nic_passport_number] ||
                selectedBooking.nic_passport_number}
            </p>
            <p>
              <strong>Check-in:</strong> {formatToDisplayDate(selectedBooking.checkin_date)}
            </p>
            <p>
              <strong>Check-out:</strong> {formatToDisplayDate(selectedBooking.checkout_date)}
            </p>
            <p>
              <strong>Status:</strong> {selectedBooking.status}
            </p>
          </div>
        )}

        {/* Cancel Button */}
        <button
          style={{ marginTop: "1rem" }}
          disabled={!selectedBooking}
          onClick={() => {
            const booking = bookings.find(
              (b) => b.booking_id.toString() === selectedBookingId
            );
            if (booking) {
              handleCancelBooking(
                booking.booking_id,
                booking.room_number
            )}
          }}
        >
          Cancel Booking
        </button>
      </div>
    )}
    {action === "Upcoming Booking" && (
      <div>
        <h3>📅 Upcoming Bookings</h3>
        {bookings.map((b) => (
          <div
            key={b.booking_id}
            style={{
              border: "1px solid #ccc",
              marginBottom: "10px",
              padding: "10px",
              display: "flex",
              flexWrap: "wrap",
              gap: "10px",
            }}
          >
            {/* 1st Row: NIC & Guest Name */}
            <div style={{ width: "48%" }}>
              <strong>NIC:</strong> {b.nic_passport_number}
            </div>
            <div style={{ width: "48%" }}>
              <strong>Guest Name:</strong> {guestNames[b.nic_passport_number] || b.nic_passport_number}
            </div>

            {/* 2nd Row: Check-in & Check-out */}
            <div style={{ width: "48%" }}>
              <strong>Check-in:</strong> {formatToDisplayDate(b.checkin_date)}
            </div>
            <div style={{ width: "48%" }}>
              <strong>Check-out:</strong> {formatToDisplayDate(b.checkout_date)}
            </div>

            {/* 3rd Row: Status & Notes */}
            <div style={{ width: "48%" }}>
              <strong>Status:</strong> {b.status}
            </div>
            {b.notes && (
              <div style={{ width: "48%" }}>
                <strong>Notes:</strong> {b.notes}
              </div>
            )}
          </div>
        ))}
      </div>
    )}
    </div>
  )}


export default BookingManagement;
