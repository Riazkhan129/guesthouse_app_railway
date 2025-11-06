// src/components/Billing.js
import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import API from "../api";
import '../styles/global.css';

const formatCurrency = (value) => {
  const num = Number(value);
  return isNaN(num) ? "Rs. 0" : `Rs. ${num.toLocaleString()}`;
};

function Billing({ selectedBooking, guest, roomPrice, totalNights, roomServiceSummary, roomServiceItemsByDate, onCheckoutComplete }) {

  // const { token } = useContext(AuthContext);
  // const { clientId } = useContext(AuthContext);
  const { token, clientId } = useContext(AuthContext);

  const [laundry, setLaundry] = useState(0);
  const [meals, setMeals] = useState(0);
  const [damages, setDamages] = useState(0);
  const [showInvoice, setShowInvoice] = useState(false);
  const [checkoutComplete, setCheckoutComplete] = useState(false);
  const [error, setError] = useState("");
  const [companyLogo, setCompanyLogo] = useState([]);
  const [companyName, setCompanyName] = useState("Loading...");

  if (!selectedBooking || !guest || !clientId) return null;
//  if (!token || !selectedBooking || !guest) return null;

  const roomCharges = roomPrice * totalNights;
  const extraCharges = roomServiceSummary?.reduce((sum, item) => sum + item.total_amount, 0) || 0;
  const totalAmount = roomCharges + extraCharges;
  const payment = selectedBooking.advance_payment || 0;
  const balance = totalAmount - payment;

  const formatDateTime = (isoDateStr) => {
  if (!isoDateStr) return "";
  const date = new Date(isoDateStr);
  console.log("date =", date)
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
    const bookingId = selectedBooking.booking_id;
    const roomNumber = selectedBooking.room_number;
    try {
      console.log("🚀 Starting checkout for booking:", bookingId);
      const headers = {
        "X-Client-ID": clientId}
      // const headers = { Authorization: `Bearer ${token}` };

    // Vacant the room
    await API.put(`/rooms/update_status/${roomNumber}?status=vacant`, {}, { headers });
    console.log("✅ Room marked vacant");

    // Save invoice
    const invoicePayload = {
      guest_nic: selectedBooking.nic_passport_number,
      guest_name: guest.name,
      room_number: roomNumber,
      room_price: roomPrice,
      checkin_date: selectedBooking.actual_checkin_time,
      checkout_date: new Date().toISOString().split("T")[0],
      total_nights: totalNights,
      room_charges: roomCharges,
      laundry,
      meals,
      damages,
      total_amount: totalAmount,
      advance: payment,
      balance_paid: balance,
      booking_id: bookingId,
    };

    const invoiceRes = await API.post("/invoices/", invoicePayload, { headers });
    console.log("🧾 Full invoice response:", invoiceRes.data);

    const invoiceId = invoiceRes.data.invoice_id;
    
    // Update booking
    const bookingUpdatePayload = {
      actual_checkout_time: `${new Date().toISOString().split("T")[0]} ${new Date().toTimeString().split(" ")[0]}`,
      // actual_checkout_date: new Date().toISOString().split("T")[0],
      total_payment: totalAmount,
      invoice_id: invoiceId,
      status: "checked_out"
    };

    const bookingUpdateRes = await API.put(`/checkout/update_booking/${bookingId}`, bookingUpdatePayload, { headers });
    console.log("✅ Booking updated successfully");

    setCheckoutComplete(true);
    setError("");
    alert("✔️ Checkout complete and invoice saved!");

    // 🔧 UPDATED: Notify parent to reset view
      if (onCheckoutComplete) {
        onCheckoutComplete();
      }

  } catch (err) {
    console.error("❌ Checkout error:", err);
    setError("❌ Checkout failed. Please try again.");
  }
};

  return (
    <div>
      <h2>Other Charges</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {roomServiceSummary.length > 0 && (
        <div style={{ marginTop: "20px" }}>
        {roomServiceSummary.reduce((rows, item, index) => {
          if (index % 2 === 0) {
            rows.push([item]); // start new row
          } else {
            rows[rows.length - 1].push(item); // add to current row
          }
          return rows;
        }, []).map((row, rowIndex) => (
          <div key={rowIndex} style={{ display: "flex", gap: "40px", marginBottom: "15px" }}>
            {row.map((item, colIndex) => (
              <div key={colIndex} style={{ display: "flex", alignItems: "center", flex: 1, gap: "10px" }}>
                <label style={{ fontWeight: "bold", whiteSpace: "nowrap" }}>
                  {item.category_name} Charges:
                </label>
                <input
                  type="number"
                  value={item.total_amount}
                  readOnly
                  style={{
                    padding: "8px",
                    width: "100%",
                    maxWidth: "150px",
                    backgroundColor: "#f0f0f0",
                    border: "1px solid #ccc",
                    color: "#333"
                  }}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
      )}

      

      <br /><br />
      <button onClick={renderInvoice}>🧾 Preview Invoice</button>

      {showInvoice && (
        <div id="print-section" style={{ border: "1px solid #ccc", padding: "20px", marginTop: "20px" }}>
          <div style={{ textAlign: "center", marginBottom: "30px" }}>
            <img
              src={companyLogo} // ✅ Replace with your actual logo path
              alt="Guest House Logo"
              style={{ height: "60px", marginBottom: "10px" }}
            />
            <h2 style={{ margin: 0, fontSize: "24px" }}>{companyName}</h2> {/* ✅ Replace with your actual name */}
          </div>

          {/* Static rows */}
        {[
          { label1: "Name:", value1: guest.name, label2: "NIC:", value2: selectedBooking.nic_passport_number },
          { label1: "Room:", value1: selectedBooking.room_number, label2: "Check-in:", value2: formatDateTime(selectedBooking.actual_checkin_time) },
          { label1: "Nights:", value1: totalNights, label2: "Room Charges:", value2: formatCurrency(roomCharges) },
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

        {/* ✅ Dynamic room service charges */}
        {roomServiceSummary?.length > 0 &&
          roomServiceSummary.reduce((rows, item, index) => {
            if (index % 2 === 0) {
              rows.push([item]);
            } else {
              rows[rows.length - 1].push(item);
            }
            return rows;
          }, []).map((pair, idx) => (
            <div key={`service-${idx}`} style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
              {pair.map((item, i) => (
                <div key={i} style={{ display: "flex", width: "45%" }}>
                  <div style={{ width: "120px", fontWeight: "bold" }}>{item.category_name}:</div>
                  <div>{formatCurrency(item.total_amount)}</div>
                </div>
              ))}
            </div>
        ))}

        

        {/* Final totals */}
        {[
          { label1: "Total:", value1: formatCurrency(totalAmount), label2: "Advance:", value2: formatCurrency(payment) },
          { label1: "Balance to Pay:", value1: formatCurrency(balance), label2: "", value2: "" },
        ].map((row, idx) => (
          <div key={`total-${idx}`} style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
            <div style={{ display: "flex", width: "45%" }}>
              <div style={{ width: "120px", fontWeight: "bold" }}>{row.label1}</div>
              <div>{row.value1}</div>
            </div>
            {row.label2 && (
              <div style={{ display: "flex", width: "45%" }}>
                <div style={{ width: "120px", fontWeight: "bold" }}>{row.label2}</div>
                <div>{row.value2}</div>
              </div>
            )}
          </div>
        ))}

        {roomServiceItemsByDate.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <hr style={{ margin: "30px 0", borderTop: "2px solid #ccc" }} />
          <h4>📅 Room Service Details by Date</h4>
          {roomServiceItemsByDate.map((entry, index) => (
            <div key={index} style={{ marginBottom: "15px" }}>
              <strong>{formatDateTime(entry.date).split(" - ")[0]}</strong>
              {entry.items
                .slice() // ✅ Create a shallow copy to avoid mutating original
                .sort((a, b) => a.expense_item_id - b.expense_item_id) // ✅ Sort by expense_item_id
                .map((item, i) => (
                  <span key={i} style={{ marginLeft: "15px" }}>
                    {item.expense_name}: Rs. {item.total_price.toLocaleString()}
                  </span>
              ))}
            </div>
          ))}
        </div>
      )}
        </div>
      )}

      
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        {showInvoice && (
          <button onClick={printInvoice} style={{ background: "#4CAF50", color: "white", padding: "10px 20px", border: "none", cursor: "pointer", fontSize: "16px" }}>
            🖨️ Print Receipt
          </button>
        )}
        <button onClick={handleCheckout}>✅ Confirm Checkout & Save Invoice</button>
        {checkoutComplete && <p style={{ color: "green" }}>✔ Guest checked out and invoice saved.</p>}
      </div>
    </div>
  );
}

export default Billing;
