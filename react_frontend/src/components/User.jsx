import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

function UserManager() {
  const { token } = useContext(AuthContext);

  //const headers = { Authorization: `Bearer ${token}` };

  const [users, setUsers] = useState([]);
  const [action, setAction] = useState("View");
  const [formData, setFormData] = useState(initialFormState());
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [passwordVisibility, setPasswordVisibility] = useState({});

  function initialFormState() {
    return {
      name: "",
      username: "",
      password: "",
      role: "Front Desk",
    };
  }

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    // Reset form when action changes
    setFormData(initialFormState());
    setSelectedUserId(null);
  }, [action]);

  const fetchUsers = async () => {
    try {
      const res = await API.get("/users/", {
        headers: { Authorization: `Bearer ${token}` } // 🔧 UPDATED
      });
      if (res.status === 200) setUsers(res.data);
    } catch (err) {
      alert("❌ Failed to fetch users.");
    }
  };

  const handleAddUser = async () => {
    try {
      const res = await API.post("/users/add", formData, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 UPDATED
      });
      if (res.status === 200) {
        alert("✅ User added!");
        fetchUsers();
        setFormData(initialFormState());
      } else {
        alert("❌ Failed to add user");
      }
    } catch (err) {
      alert("❌ Error adding user.");
      console.error(err);
    }
  };

  const handleUpdateUser = async () => {
    try {
      const res = await API.put(`/users/update/${selectedUserId}`, formData, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 UPDATED
      });
       if (res.status === 200) {
        alert("✅ User updated!");
        fetchUsers();
        setSelectedUserId(null);
        setFormData(initialFormState());
      } else {
        alert("❌ Update failed");
      }
    } catch (err) {
      alert("❌ Error updating user.");
      console.error(err);
    }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      const res = await API.delete(`/users/delete/${id}`, {
        headers: { Authorization: `Bearer ${token}` } // 🔧 UPDATED
      });

      if (res.status === 200) {
        alert("🗑️ User deleted!");
        fetchUsers();
        setSelectedUserId(null);
      }
    } catch (err) {
      alert("❌ Error deleting user.");
      console.error(err);
    }
  };

  const handleUserSelection = (id) => {
    const user = users.find((u) => u.user_id === id);
    if (user) {
      setFormData({
        name: user.name || "",
        username: user.username || "",
        password: user.password || "",
        role: user.role || "Front Desk",
      });
      setSelectedUserId(id);
    }
  };

  const togglePassword = (index) => {
    setPasswordVisibility((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const inputStyle = {
    padding: "8px",
    margin: "6px 0",
    width: "100%",
    maxWidth: "300px",
    display: "block",
  };

  const buttonStyle = {
    padding: "8px 12px",
    marginTop: "10px",
    backgroundColor: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  };

  const selectStyle = {
    ...inputStyle,
  };

  return (
    <div>
      <h2>👤 User Management</h2>

      {/* Action Selector */}
      <div style={{ marginBottom: "20px" }}>
        <label><strong>Select Action:</strong></label>
        <div style={{ display: "flex", gap: "1.5rem", marginTop: "10px" }}>
          {["Add", "View", "Update", "Delete"].map((option) => (
            <label key={option}>
              <input
                type="radio"
                name="user-action"
                value={option}
                checked={action === option}
                onChange={(e) => setAction(e.target.value)}
                style={{ marginRight: "6px" }}
              />
              {option}
            </label>
          ))}
        </div>
      </div>

      {/* ----------- ADD ----------- */}
      {action === "Add" && (
        <div>
          <h3>➕ Add New User</h3>
          <input
            style={inputStyle}
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            style={inputStyle}
            placeholder="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          />
          <input
            style={inputStyle}
            type="text"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <select
            style={selectStyle}
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          >
            <option>Front Desk</option>
            <option>Management</option>
          </select>
          <button style={buttonStyle} onClick={handleAddUser}>Create User</button>
        </div>
      )}

      {/* ----------- VIEW ----------- */}
      {action === "View" && (
        <div>
          <h3>👀 All Users</h3>
          {users.map((u, index) => (
            <div key={u.user_id} style={{ borderBottom: "1px solid #ccc", padding: "10px 0" }}>
              <p><b>Name:</b> {u.name}</p>
              <p><b>Username:</b> {u.username}</p>
              <p>
                <b>Password:</b>{" "}
                {passwordVisibility[index] ? u.password : "••••••••"}
                <button onClick={() => togglePassword(index)} style={{ marginLeft: "10px" }}>👁️</button>
              </p>
              <p><b>Role:</b> {u.role}</p>
            </div>
          ))}
        </div>
      )}

      {/* ----------- UPDATE ----------- */}
      {action === "Update" && (
        <div>
          <h3>✏️ Update User</h3>
          <select style={selectStyle} onChange={(e) => handleUserSelection(parseInt(e.target.value))}>
            <option>Select User</option>
            {users.map((u) => (
              <option key={u.user_id} value={u.user_id}>{u.user_id} - {u.username}</option>
            ))}
          </select>
          {selectedUserId && (
            <>
              <input
                style={inputStyle}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <input
                style={inputStyle}
                type="text"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
              <select
                style={selectStyle}
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <option>Front Desk</option>
                <option>Management</option>
              </select>
              <button style={buttonStyle} onClick={handleUpdateUser}>Update User</button>
            </>
          )}
        </div>
      )}

      {/* ----------- DELETE ----------- */}
      {action === "Delete" && (
        <div>
          <h3>🗑️ Delete User</h3>
          <select style={selectStyle} onChange={(e) => setSelectedUserId(parseInt(e.target.value))}>
            <option>Select User</option>
            {users.map((u) => (
              <option key={u.user_id} value={u.user_id}>
                {u.user_id} - {u.username}
              </option>
            ))}
          </select>
          {selectedUserId && (
            <button
              style={{ ...buttonStyle, backgroundColor: "#dc3545" }}
              onClick={() => handleDeleteUser(selectedUserId)}
            >
              Confirm Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default UserManager;
