import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

export default function RoomService() {
  const [mode, setMode] = useState("add"); // ✅ Mode toggle
  const [bookings, setBookings] = useState([]);
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [openRequests, setOpenRequests] = useState([]); // ✅ Open room service records
  const [statusOptions] = useState(["Delivered", "Canceled"]);
  const { token } = useContext(AuthContext);
  const headers = { Authorization: `Bearer ${token}` };

  const [form, setForm] = useState({
    booking_id: "",
    room_id: "",
    nic_passport_number: "",
    category_id: "",
    expense_item_id: "",
    quantity: 1,
    unit_price: 0,
    notes: "",
    status: ""
  });

  const [serviceId, setServiceId] = useState(null); // ✅ Track selected service record

  useEffect(() => {
  const headers = { Authorization: `Bearer ${token}` }; // ✅ Centralized headers

  API.get("/roomservice/checkedin", { headers })
    .then(res => setBookings(res.data))
    .catch(err => console.error("❌ Error fetching bookings:", err));

  API.get("/expenseitems/expense_categories/items", { headers })
    .then(res => setItems(res.data))
    .catch(err => console.error("❌ Error fetching items:", err));

  API.get("/expensecategories/categories", { headers })
    .then(res => setCategories(res.data))
    .catch(err => console.error("❌ Error fetching categories:", err));

  API.get("/roomservice/open", { headers }) // ✅ FIXED: removed stray comma and added headers correctly
    .then(res => setOpenRequests(res.data))
    .catch(err => {
      console.error("❌ Error fetching open room services:", err);
      alert("❌ Error fetching open room services");
    });
}, []);

  const getCategoryName = (id) => {
    const cat = categories.find(c => c.id === id);
    return cat ? cat.category_name : "Unknown";
  };

  const handleOpenRequestSelect = (id) => {
    const selected = openRequests.find(r => r.id === parseInt(id));
    if (selected) {
      setServiceId(selected.id);
      setForm({
        booking_id: selected.booking_id,
        room_id: selected.room_id,
        nic_passport_number: selected.nic_passport_number,
        category_id: selected.category_id,
        expense_item_id: selected.expense_item_id,
        quantity: selected.quantity,
        unit_price: selected.unit_price,
        notes: selected.notes,
        status: ""
      });
    } else {
      console.warn("⚠️ No matching open request found for ID:", id); // ✅ Fallback log
    }
  };

  const handleBookingSelect = (bookingId) => {
    const selected = bookings.find(b => b.booking_id === parseInt(bookingId));
    if (selected) {
      setForm({
        ...form,
        booking_id: selected.booking_id,
        room_id: selected.room_number,
        nic_passport_number: selected.nic_passport_number
      });
    }
  };

  const handleSubmit = async () => {
    if (mode === "add") {
      const payload = {
        ...form,
        total_price: form.quantity * form.unit_price
      };
      await API.post("/roomservice/create", payload);
      alert("✅ Room service request submitted");
    } else if (mode === "update") {
      if (!form.status) return alert("⚠️ Please select a status.");
      await API.put(`/roomservice/update/${serviceId}`, { status: form.status });
      alert("✅ Room service status updated");

      // ✅ Refresh open requests
      API.get("/roomservice/open", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => setOpenRequests(res.data))
        .catch(err => console.error("❌ Error refreshing open requests:", err));
    }

    setForm({
      booking_id: "",
      room_id: "",
      nic_passport_number: "",
      category_id: "",
      expense_item_id: "",
      quantity: 1,
      unit_price: 0,
      notes: "",
      status: ""
    });
    setServiceId(null); // ✅ Reset only after successful update
  };

  return (
    <div>
      <h3>🛎️ Room Service Request</h3>

      {/* ✅ Mode Toggle */}
      <div style={{ marginBottom: "12px" }}>
        {["add", "update"].map(m => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setForm({
                booking_id: "",
                room_id: "",
                nic_passport_number: "",
                category_id: "",
                expense_item_id: "",
                quantity: 1,
                unit_price: 0,
                notes: "",
                status: ""
              });
              setServiceId(null);
            }}
            style={{
              marginRight: "8px",
              backgroundColor: mode === m ? "#007bff" : "#f0f0f0",
              color: mode === m ? "#fff" : "#000",
              border: "1px solid #ccc",
              padding: "6px 12px",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            {m.toUpperCase()}
          </button>
        ))}
      </div>

      {/* ✅ Update Mode: Select Open Room Service */}
      {mode === "update" && (
        <label style={{ display: "block", marginBottom: "12px" }}>
          Select Open Room Service Request:
          <select
            value={serviceId || ""}
            onChange={e => handleOpenRequestSelect(e.target.value)}
            style={{ width: "200px", marginLeft: "12px" }}
          >
            <option value="">-- Select Room Service --</option>
            {openRequests.map(r => (
              <option key={r.id} value={r.id}>
                Room {r.room_id}
              </option>
            ))}
          </select>
        </label>
      )}

      {/* 🔹 Room + Item Fields */}
      <div style={{ display: "flex", gap: "100px", marginBottom: "12px" }}>
        <label>
          Room :
          <select
            value={form.booking_id || ""}
            onChange={e => handleBookingSelect(e.target.value)}
            style={{ width: "280px" }}
            disabled={mode === "update"}
          >
            <option value="">-- Select Checked-in Room --</option>
            {bookings.map(b => (
              <option key={b.booking_id} value={b.booking_id}>
                Room {b.room_number} — {b.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Item :
          <select
            value={form.expense_item_id || ""}
            onChange={e => {
              const selected = items.find(i => i.expense_item_id === parseInt(e.target.value));
              if (selected) {
                setForm({
                  ...form,
                  expense_item_id: selected.expense_item_id,
                  category_id: selected.category_id
                });
              }
            }}
            style={{ width: "280px" }}
            disabled={mode === "update"}
          >
            <option value="">-- Select Item --</option>
            {items.map(i => (
              <option key={i.expense_item_id} value={i.expense_item_id}>
                {getCategoryName(i.category_id)} — {i.expense_name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* 🔹 Quantity + Price */}
      <div style={{ display: "flex", gap: "100px", marginBottom: "12px" }}>
        <label>
          Quantity :
          <input
            type="number"
            value={form.quantity}
            onChange={e => setForm({ ...form, quantity: parseInt(e.target.value) })}
            style={{ width: "100px" }}
            disabled={mode === "update"}
          />
        </label>

        <label>
          Unit Price :
          <input
            type="number"
            value={form.unit_price}
            onChange={e => setForm({ ...form, unit_price: parseInt(e.target.value) })}
            style={{ width: "100px" }}
            disabled={mode === "update"}
          />
        </label>

        <label>
          Total Amount :
          <input
            type="number"
            value={form.quantity * form.unit_price}
            disabled
            style={{ width: "120px", backgroundColor: "#f0f0f0" }}
          />
        </label>
      </div>

      {/* 🔹 Notes */}
      <label>
        Notes :
        <input
          type="text"
          value={form.notes}
          onChange={e => setForm({ ...form, notes: e.target.value })}
          style={{
            width: "600px",
            marginBottom: "12px",
            padding: "8px",
            fontSize: "14px"
          }}
          disabled={mode === "update"}
        />
      </label>

    {/* ✅ Status Dropdown for Update */}
    {mode === "update" && (
      <label style={{ display: "block", marginTop: "12px", marginBottom: "12px" }}>
        Status :
        <select
          value={form.status}
          onChange={e => setForm({ ...form, status: e.target.value })}
          style={{ width: "280px", marginLeft: "12px" }}
        >
          <option value="">-- Select Status --</option>
          {statusOptions.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </label>
    )}
    
    <div style={{ textAlign: "center", marginTop: "16px" }}>
      <button onClick={handleSubmit}>Submit</button>
    </div>
    </div>
  )}