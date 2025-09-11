// src/components/Billing.js
import React, { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import 'D:/guesthouse_app/react_frontend/src/styles/global.css';
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

const API_URL = "http://localhost:8000"; // define once for clarity

// ...inside your Billing component JSX
<ToastContainer position="top-right" autoClose={3000} hideProgressBar />


const formatCurrency = (value) => {
  const num = Number(value);
  return isNaN(num) ? "Rs. 0" : `Rs. ${num.toLocaleString()}`;
};

function Billing({ selectedBooking, guest, roomPrice, totalNights }) {
  const { token } = useContext(AuthContext);

  const [laundry, setLaundry] = useState(0);
  const [meals, setMeals] = useState(0);
  const [damages, setDamages] = useState(0);
  const [showInvoice, setShowInvoice] = useState(false);
  const [checkoutComplete, setCheckoutComplete] = useState(false);
  const [error, setError] = useState("");

  if (!token || !selectedBooking || !guest) return null;

  const roomCharges = roomPrice * totalNights;
  const extraCharges = laundry + meals + damages;
  const totalAmount = roomCharges + extraCharges;
  const payment = selectedBooking.advance_payment || 0;
  const balance = totalAmount - payment;

  const renderInvoice = () => {
    setShowInvoice(true);
    setError(""); // Reset any previous errors
  };

  const printInvoice = () => {
    const content = document.getElementById("print-section").innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Print Invoice</title>
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

  const handleCheckout = async () => {
    console.log("🔥 handleCheckout triggered!");
  const bookingId = selectedBooking.booking_id;
  const roomNumber = selectedBooking.room_number;
  const headers = { Authorization: `Bearer ${token}` };
  const checkoutDate = new Date().toISOString().split("T")[0];

  let invoiceId = null;

  // Step 1: Update room status
  console.log("🔁 Step 1: Updating room status…");
  try {
    console.log("🛠 Step 1: Sending room update request…");
    const res1 = await axios.put(`${API_URL}/rooms/update_status/${roomNumber}?status=vacant`, {}, { headers });
    toast.success("Room marked as vacant");
  } catch (err) {
    console.log("❌ Step 1 failed:", err.message);
    console.error("❌ Room status update failed:", err.response?.data || err.message);
    toast.error("Failed to update room status");
    return;
  }

  // Step 2: Create invoice
  const invoicePayload = {
    booking_id: bookingId,
    guest_nic: selectedBooking.nic_passport_number,
    guest_name: guest.name,
    room_number: roomNumber,
    room_price: roomPrice,
    checkin_date: selectedBooking.checkin_date,
    checkout_date: checkoutDate,
    total_nights: totalNights,
    room_charges: roomCharges,
    laundry,
    meals,
    damages,
    total_amount: totalAmount,
    advance: payment,
    balance_paid: balance
  };

  console.log("🔁 Step 2: Saving invoice…");
  try {
    const res2 = await axios.post(`${API_URL}/invoices/`, invoicePayload, { headers });
    invoiceId = res2.data.invoice_id;
    console.log("✅ Invoice response:", res2.data);
    toast.success("Invoice saved");
  } catch (err) {
    console.error("❌ Invoice save failed:", err.response?.data || err.message);
    toast.error("Failed to save invoice");
    return;
  }

  // Step 3: Update booking
  const bookingUpdatePayload = {
    actual_checkout_date: checkoutDate,
    total_payment: totalAmount,
    invoice_id: invoiceId,
    status: "checked_out"
  };

  console.log("🔁 Step 3: Updating booking…");
  try {
    const res3 = await axios.put(`${API_URL}/checkout/update_booking/${bookingId}`, bookingUpdatePayload, { headers });
    console.log("✅ Booking update response:", res3.data);
    toast.success("Booking updated");
    setCheckoutComplete(true);
    setError("");
  } catch (err) {
    console.error("❌ Booking update failed:", err.response?.data || err.message);
    toast.error("Failed to update booking");
    return;
  }
};


  return (
    <div>
      <h2>Other Charges</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <label>Laundry Charges</label>
      <input type="number" value={laundry} onChange={(e) => setLaundry(Number(e.target.value))} />

      <label>Meal Charges</label>
      <input type="number" value={meals} onChange={(e) => setMeals(Number(e.target.value))} />

      <label>Damage Charges</label>
      <input type="number" value={damages} onChange={(e) => setDamages(Number(e.target.value))} />

      <br /><br />
      <button onClick={renderInvoice}>🧾 Preview Invoice</button>

      {showInvoice && (
        <div id="print-section" style={{ border: "1px solid #ccc", padding: "20px", marginTop: "20px" }}>
          <h2 style={{ textAlign: "center", marginBottom: "30px" }}>🧾 Guest Invoice</h2>

          {[
            { label1: "Name:", value1: guest.name, label2: "NIC:", value2: selectedBooking.nic_passport_number },
            { label1: "Room:", value1: selectedBooking.room_number, label2: "Check-in:", value2: selectedBooking.checkin_date },
            { label1: "Nights:", value1: totalNights, label2: "Room Charges:", value2: formatCurrency(roomCharges) },
            { label1: "Laundry:", value1: formatCurrency(laundry), label2: "Meals:", value2: formatCurrency(meals) },
            { label1: "Damages:", value1: formatCurrency(damages), label2: "Total:", value2: formatCurrency(totalAmount) },
            { label1: "Advance:", value1: formatCurrency(payment), label2: "Balance to Pay:", value2: formatCurrency(balance) },
          ].map((row, idx) => (
            <div key={idx} style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
              <div style={{ display: "flex", width: "45%" }}>
                <div style={{ width: "120px", fontWeight: "bold" }}>{row.label1}</div>
                <div>{row.value1}</div>
              </div>
              <div style={{ display: "flex", width: "45%" }}>
                <div style={{ width: "120px", fontWeight: "bold" }}>{row.label2}</div>
                <div>{row.value2}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ textAlign: "center", marginTop: "20px" }}>
        {showInvoice && (
          <button onClick={printInvoice} style={{ background: "#4CAF50", color: "white", padding: "10px 20px", border: "none", cursor: "pointer", fontSize: "16px" }}>
            🖨️ Print Receipt
          </button>
        )}

        <br />
        <button onClick={() => console.log("✅ Button clicked!")}>
          Try Me
        </button>

        <button onClick={handleCheckout}>✅ Confirm Checkout & Save Invoice</button>
        {checkoutComplete && <p style={{ color: "green" }}>✔ Guest checked out and invoice saved.</p>}
      </div>
    </div>
  );
}

export default Billing;
