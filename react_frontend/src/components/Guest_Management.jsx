import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext"; // ✅ ADDED
import API from "../api"; // ✅ ADDED

const blankGuestForm = {
  nic_passport_number: "",
  name: "",
  contact: "",
  email: "",
  emergency_contact: "",
  nationality: "",
  guest_type: "",
  address: "",
  corporate_name: "",             // 🔧 NEW
  corporate_contact_person: "",   // 🔧 NEW
  corporate_address: "",          // 🔧 NEW
};

const GuestForm = ({ form, onChange, editable = true, onSubmit, buttonLabel }) => {
  const guest_type = form?.guest_type || "";
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", maxWidth: "800px", marginTop: "20px" }}>
      {["nic_passport_number", "name", "contact", "email", "emergency_contact", "nationality"].map((key) => (
        <div key={key}>
          <label>{key.replace(/_/g, " ").toUpperCase()}:</label>
          <input
            name={key}
            value={form?.[key] ?? ""}
            onChange={onChange}
            readOnly={!editable && key === "nic_passport_number"}
            style={{ width: "100%", padding: "6px" }}
          />
        </div>
      ))}
      <div>
        <label>Guest Type:</label>
        <select name="guest_type" value={guest_type} onChange={onChange} style={{ width: "100%", padding: "6px" }}>
          <option value="">Select Type</option>
          {["Individual", "Corporate", "VIP"].map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Address:</label>
        <textarea name="address" rows={3} value={form?.address || ""} onChange={onChange} style={{ width: "100%" }} />
      </div>

      {/* 🔧 CORPORATE FIELDS */}
      {guest_type === "Corporate" && (
        <>
          <div>
            <label>Corporate Name:</label>
            <input
              name="corporate_name"
              value={form?.corporate_name || ""}
              onChange={onChange}
              style={{ width: "100%", padding: "6px" }}
            />
          </div>
          <div>
            <label>Contact Person:</label>
            <input
              name="corporate_contact_person"
              value={form?.corporate_contact_person || ""}
              onChange={onChange}
              style={{ width: "100%", padding: "6px" }}
            />
          </div>
          <div>
            <label>Corporate Address:</label>
            <textarea
              name="corporate_address"
              rows={3}
              value={form?.corporate_address || ""}
              onChange={onChange}
              style={{ width: "100%" }}
            />
          </div>
        </>
      )}
      <div style={{ gridColumn: "span 2" }}>
        <button onClick={onSubmit} style={{ padding: "8px 16px" }}>{buttonLabel}</button>
      </div>
    </div>
  );
};
const GuestManagement = () => {
  const { token } = useContext(AuthContext); // ✅ ADDED

  const [guests, setGuests] = useState([]);
  const [form, setForm] = useState({ ...blankGuestForm });
  const [selectedGuest, setSelectedGuest] = useState("");
  const [nicToDelete, setNicToDelete] = useState("");
  const [guestToDelete, setGuestToDelete] = useState(null);
  const [action, setAction] = useState("Create");

  useEffect(() => {
  if (action === "Create") {
    resetForm();
  } else if (["Update", "View", "Delete"].includes(action)) {
    fetchGuests();
  }
}, [action]);


  useEffect(() => {
    if (selectedGuest) {
      API.get(`/guests/search/${selectedGuest}`, {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      })
        .then((res) => setForm({ ...res.data }))
        .catch(() => alert("❌ Guest not found"));
    }
  }, [selectedGuest]);

  const resetForm = () => {
    setForm({ ...blankGuestForm });
    setSelectedGuest("");
    setGuestToDelete(null);
    setNicToDelete("");
  };

  const fetchGuests = () => {
    API.get("/guests/all", {
      headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
    })
      .then((res) => setGuests(res.data))
      .catch(() => alert("❌ Failed to load guests"));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreate = () => {
    API.post("/guests/", form, {
      headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
    })
      .then(() => {
        alert("✅ Guest created successfully");
        setGuests((prev) => [...prev, form]);
        resetForm();
      })
      .catch(() => alert("❌ Failed to create guest"));
  };

  const handleUpdate = () => {
    API.put(`/guests/update/${form.nic_passport_number}`, form, {
      headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
    })
       .then(() => {
        alert("✅ Guest updated");
        resetForm();
      })
      .catch(() => alert("❌ Update failed"));
  };

  const handleDeleteSearch = () => {
    API.get(`/guests/search/${nicToDelete}`, {
      headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
    })
      .then((res) => setGuestToDelete(res.data))
      .catch(() => alert("❌ Guest not found"));
  };

  const handleDelete = () => {
    API.delete(`/guests/delete/${nicToDelete}`, {
      headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
    })
      .then(() => {
        alert("✅ Deleted successfully");
        resetForm();
      })
      .catch(() => alert("❌ Failed to delete guest"));
  };

  

  return (
    <div style={{ padding: "20px" }}>
      <h2>👤 Guest Management</h2>

      {/* Action Selector */}
      <div style={{ marginBottom: "20px", display: "flex", gap: "20px", flexWrap: "nowrap" }}>
        {["Create", "Update", "Delete", "View"].map((act) => (
          <label key={act} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <input
              type="radio"
              name="action"
              value={act}
              checked={action === act}
              onChange={(e) => setAction(e.target.value)}
            />
            {act}
          </label>
        ))}
      </div>

      {/* Create */}
      

      {action === "Create" && (
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GuestForm
            form={form}
            onChange={handleChange}
            onSubmit={handleCreate}
            buttonLabel="✅ Create Guest"
          />
        </div>
      )}

      {/* Update */}
      {action === "Update" && (
        <div>
          <label>Select Guest:</label>
          <select value={selectedGuest} onChange={(e) => setSelectedGuest(e.target.value)} style={{ marginLeft: "10px" }}>
            <option value="">-- Choose --</option>
            {guests.map((g) => (
              <option key={g.nic_passport_number} value={g.nic_passport_number}>
                {g.nic_passport_number} - {g.name}
              </option>
            ))}
          </select>
          {form.nic_passport_number && (
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginTop: "30px"
              }}
            >
            <GuestForm
              form={form}
              onChange={handleChange}
              onSubmit={handleUpdate}
              editable={false}
              buttonLabel="✏️ Update Guest"
            />
          </div>
          )}
        </div>
      )}

      {/* Delete */}
      {action === "Delete" && (
        <div style={{ marginTop: "20px" }}>
          <input
            placeholder="NIC / Passport"
            value={nicToDelete}
            onChange={(e) => setNicToDelete(e.target.value)}
            style={{ marginRight: "10px" }}
          />
          <button onClick={handleDeleteSearch}>🔍 Search</button>

          {guestToDelete && (
            <div style={{ marginTop: "20px", border: "1px solid red", padding: "10px", backgroundColor: "#fff5f5" }}>
              <h4>Confirm Delete</h4>
              {Object.entries(guestToDelete).map(([k, v]) => (
                <p key={k}><b>{k.replace(/_/g, " ")}:</b> {v}</p>
              ))}
              <button onClick={handleDelete} style={{ backgroundColor: "red", color: "white", marginTop: "10px" }}>
                🗑️ Delete Guest
              </button>
            </div>
          )}
        </div>
      )}

      {/* View All */}
      {action === "View" && (
        <div>
          {guests.map((g, i) => (
            <div key={g.nic_passport_number} style={{ border: "1px solid #ccc", marginBottom: "10px", padding: "10px" }}>
              <h4>Guest #{i + 1}</h4>
              {Object.entries(g).map(([k, v]) => (
                <p key={k}><b>{k.replace(/_/g, " ")}:</b> {v}</p>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GuestManagement;
