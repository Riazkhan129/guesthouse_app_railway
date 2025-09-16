import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import API from "../api"; // ✅ ADDED: Centralized Axios instance

const Rooms = () => {
  const { token } = useContext(AuthContext);

  // const headers = { Authorization: `Bearer ${token}` };
  // const API_URL = "http://localhost:8000";

  const [rooms, setRooms] = useState([]);
  const [newRoom, setNewRoom] = useState({
    room_number: "",
    type: "Single",
    price: 0,
    notes: "",
    status: "vacant",
  });

  const [editMode, setEditMode] = useState(null);
  const [editedRoom, setEditedRoom] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const res = await API.get("/rooms/", {
        headers: { Authorization: `Bearer ${token}` } // 🔧 CHANGED
      });
      if (res.status === 200) setRooms(res.data);
    } catch (err) {
      console.error("Fetch rooms failed", err);
      alert("❌ Failed to fetch rooms");
    }
  };

  const handleCreateRoom = async () => {
    try {
      setLoading(true);
      const res = await API.post("/rooms/add", {
        ...newRoom,
        price: parseFloat(newRoom.price),
      }, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 CHANGED
      });

      if (res.status === 200) {
        alert("✅ Room Added!");
        setNewRoom({ room_number: "", type: "Single", price: 0, notes: "", status: "vacant" });
        fetchRooms();
      }
    } catch (err) {
      console.error(err);
      if (err.response?.data?.detail) {
        alert("❌ " + err.response.data.detail);
      } else {
        alert("❌ Failed to create room");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRoom = async (roomNumber) => {
    if (!window.confirm(`Are you sure you want to delete Room ${roomNumber}?`)) return;

    try {
      const res = await API.delete(`/rooms/${roomNumber}`, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 CHANGED
      });
      if (res.status === 200) {
        alert("✅ Room Deleted");
        fetchRooms();
      }
    } catch (err) {
      console.error("Delete failed", err);
      alert("❌ Failed to delete room");
    }
  };

  const handleUpdateRoom = async () => {
    try {
      const res = await API.put(`/rooms/update/${editMode}`, {
        ...editedRoom,
        price: parseFloat(editedRoom.price),
      }, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 CHANGED
      });

      if (res.status === 200) {
        alert("✅ Room Updated");
        setEditMode(null);
        setEditedRoom({});
        fetchRooms();
      }
    } catch (err) {
      console.error("Update failed", err);
      alert("❌ Failed to update room");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      {/* Add Room Form */}
      <div style={{
        background: "#f9f9f9",
        padding: "20px",
        borderRadius: "8px",
        marginBottom: "30px"
      }}>
        <h3 style={{ marginBottom: "12px" }}>➕ Add New Room</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          <div><label>Room Number</label>
            <input
              style={inputStyle}
              value={newRoom.room_number}
              onChange={(e) => setNewRoom({ ...newRoom, room_number: e.target.value })}
            />
          </div>

          <div><label>Room Type</label>
            <select
              style={inputStyle}
              value={newRoom.type}
              onChange={(e) => setNewRoom({ ...newRoom, type: e.target.value })}
            >
              <option value="Single">Single</option>
              <option value="Double">Double</option>
              <option value="Suite">Suite</option>
            </select>
          </div>

          <div><label>Price</label>
            <input
              type="number"
              style={inputStyle}
              value={newRoom.price}
              onChange={(e) => setNewRoom({ ...newRoom, price: e.target.value })}
            />
          </div>

          <div><label>Notes</label>
            <input
              style={inputStyle}
              value={newRoom.notes}
              onChange={(e) => setNewRoom({ ...newRoom, notes: e.target.value })}
            />
          </div>

          <div><label>Status</label>
            <select
              style={inputStyle}
              value={newRoom.status}
              onChange={(e) => setNewRoom({ ...newRoom, status: e.target.value })}
            >
              <option value="vacant">Vacant</option>
              <option value="booked">Booked</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleCreateRoom}
          style={buttonStyle("blue")}
          disabled={loading}
        >
          {loading ? "Adding..." : "Add Room"}
        </button>
      </div>

      {/* Room List */}
      <div style={{ display: "grid", gap: "16px" }}>
        {rooms.map((room) => (
          <div key={room.room_number} style={{
            border: "1px solid #ddd",
            borderRadius: "6px",
            padding: "12px",
            background: "#fff"
          }}>
            {editMode === room.room_number ? (
              <>
              <div style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px",
                marginBottom: "10px"
              }}>
               <div>
                  <label>Type</label>
                  <input
                    style={inputStyle}
                    value={editedRoom.type}
                    onChange={(e) => setEditedRoom({ ...editedRoom, type: e.target.value })}
                  />
                </div>
                <div>
                  <label>Price</label>
                  <input
                    type="number"
                    style={inputStyle}
                    value={editedRoom.price}
                    onChange={(e) => setEditedRoom({ ...editedRoom, price: e.target.value })}
                  />
                </div>
                <div>
                  <label>Notes</label>
                  <input
                    style={inputStyle}
                    value={editedRoom.notes}
                    onChange={(e) => setEditedRoom({ ...editedRoom, notes: e.target.value })}
                  />
                </div>
                <div>
                  <label>Status</label>
                  <select
                    style={inputStyle}
                    value={editedRoom.status}
                    onChange={(e) => setEditedRoom({ ...editedRoom, status: e.target.value })}
                  >
                    <option value="vacant">Vacant</option>
                    <option value="booked">Booked</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </div>
              </div>

                  <div style={{ display: "flex", gap: "10px" }}>
                    <button style={buttonStyle("green")} onClick={handleUpdateRoom}>Save</button>
                    <button style={buttonStyle("gray")} onClick={() => { setEditMode(null); setEditedRoom({}); }}>Cancel</button>
                  </div>
              </>
            ) : (
              <>
                <div style={{ 
                  display: "grid", 
                  gridTemplateColumns: "1fr 1fr", 
                  gap: "10px",
                  lineHeight: "1.2",     // Tighten vertical spacing
                  // fontSize: "14px"       // Optional: reduce text size a bit
                }}>
                  <p style={{ margin: "4px 0" }}><strong>Room:</strong> {room.room_number}</p>
                  <p style={{ margin: "4px 0" }}><strong>Type:</strong> {room.type}</p>
                  <p style={{ margin: "4px 0" }}><strong>Price:</strong> Rs.{room.price}</p>
                  <p style={{ margin: "4px 0" }}><strong>Status:</strong> {room.status}</p>
                  <p style={{ margin: "4px 0", gridColumn: "span 2" }}>
                    <strong>Notes:</strong> {room.notes}
                  </p>
                </div>


                <div>
                  <button style={buttonStyle("orange")} onClick={() => {
                    setEditMode(room.room_number);
                    setEditedRoom({ ...room });
                  }}>Edit</button>
                  <button style={buttonStyle("red")} onClick={() => handleDeleteRoom(room.room_number)}>Delete</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// === Styles ===
const inputStyle = {
  padding: "8px",
  width: "100%",
  border: "1px solid #ccc",
  borderRadius: "4px",
};

const smallInputStyle = {
  ...inputStyle,
  marginBottom: "8px",
};

const buttonStyle = (color) => {
  const base = {
    padding: "8px 14px",
    margin: "6px 6px 0 0",
    border: "none",
    borderRadius: "4px",
    color: "white",
    cursor: "pointer",
  };

  const colors = {
    blue: { backgroundColor: "#007BFF" },
    green: { backgroundColor: "#28a745" },
    red: { backgroundColor: "#dc3545" },
    orange: { backgroundColor: "#ffc107", color: "black" },
    gray: { backgroundColor: "#6c757d" },
  };

  return { ...base, ...colors[color] };
};

export default Rooms;
