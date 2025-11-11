import React, { useEffect, useState, useContext, useRef } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

export default function ExpenseCategories() {
  const { token } = useContext(AuthContext);
  const [mode, setMode] = useState("add");
  const [categories, setCategories] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState({ category_name: "", category_active: true });
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    if (mode === "add") {
      setForm({ category_name: "", category_active: true });
      setSelectedId("");
      setError("");
      setTimeout(() => inputRef.current?.focus(), 100);
    } else if (["update", "delete"].includes(mode)) {
      const selected = categories.find(c => c.id === parseInt(selectedId));
      if (selected) {
        setForm({
          category_name: selected.category_name,
          category_active: selected.category_active
        });
        setError("");
      }
    }
  }, [mode, selectedId]);

  useEffect(() => {
    setFormSubmitted(false); // ✅ Show form again when mode changes
  }, [mode]);


  const fetchCategories = () => {
    API.get("/expense_categories/categories", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setCategories(res.data));
  };

  const handleSubmit = async () => {
    if (!form.category_name.trim()) {
      setError("Category name is required.");
      return;
    }

    let res;
    if (mode === "add") {
      res = await API.post("/expensecategories/categories", form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("✅ Category added successfully!");
    } else if (mode === "update") {
      res = await API.put(`/expensecategories/categories/${selectedId}`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("✏️ Category updated successfully!");
    } else if (mode === "delete") {
      res = await API.delete(`/expensecategories/categories/${selectedId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("🗑️ Category deleted successfully!");
    }

    fetchCategories();
    setSelectedId("");
    setFormSubmitted(true);
  };

  return (
    <div>
      <h3>📂 Expense Categories</h3>

      {/* 🔹 Mode Selector */}
      <div style={{ marginBottom: "12px" }}>
        {["add", "update", "delete", "view"].map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
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

      {/* 🔹 ADD Mode */}
      {mode === "add" && !formSubmitted && (
        <div style={{ display: "flex", gap: "24px", marginTop: "12px" }}>
          <label>
            Category :
            <input
              ref={inputRef}
              type="text"
              value={form.category_name}
              onChange={e => setForm({ ...form, category_name: e.target.value })}
              style={{ width: "220px", borderColor: error ? "red" : "#ccc" }}
            />
          </label>

          <label>
            Status
            <select
              value={form.category_active ? "true" : "false"}
              onChange={e => setForm({ ...form, category_active: e.target.value === "true" })}
              style={{ width: "140px" }}
            >
              <option value="true">Active</option>
              <option value="false">In-Active</option>
            </select>
          </label>
        </div>
      )}

      {/* 🔹 UPDATE Mode */}
      {mode === "update" && !formSubmitted && (
        <>
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ width: "220px" }}>
            <option value="">Select Category</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.category_name}</option>
            ))}
          </select>

          {selectedId && (
            <div style={{ display: "flex", gap: "24px", marginTop: "12px" }}>
              <label>
                Category :
                <input type="text" value={form.category_name} disabled style={{ width: "220px" }} />
              </label>

              <label>
                Status
                <select
                  value={form.category_active ? "true" : "false"}
                  onChange={e => setForm({ ...form, category_active: e.target.value === "true" })}
                  style={{ width: "140px" }}
                >
                  <option value="true">Active</option>
                  <option value="false">In-Active</option>
                </select>
              </label>
            </div>
          )}
        </>
      )}

      {/* 🔹 DELETE Mode */}
      {mode === "delete" && !formSubmitted && (
        <>
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ width: "220px" }}>
            <option value="">Select Category</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.category_name}</option>
            ))}
          </select>

          {selectedId && (
            <div style={{ display: "flex", gap: "24px", marginTop: "12px" }}>
              <label>
                Category :
                <input type="text" value={form.category_name} disabled style={{ width: "220px" }} />
              </label>

              <label>
                Status
                <select value={form.category_active ? "true" : "false"} disabled style={{ width: "140px" }}>
                  <option value="true">Active</option>
                  <option value="false">In-Active</option>
                </select>
              </label>
            </div>
          )}
        </>
      )}

      {/* 🔹 VIEW Mode */}
      {mode === "view" && (
        <div style={{ marginTop: "12px" }}>
          <h4>📋 All Categories</h4>
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {categories.map(c => (
              <li key={c.id} style={{ marginBottom: "8px" }}>
                <strong>{c.category_name}</strong> — {c.category_active ? "Active" : "Inactive"}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 🔹 Validation Error */}
      {error && <p style={{ color: "red", marginTop: "4px" }}>{error}</p>}

      {/* 🔹 Submit Button */}
      {mode !== "view" && !formSubmitted && (
        <div style={{ display: "flex", justifyContent: "left", marginTop: "16px", marginLeft: "200px" }}>
          <button onClick={handleSubmit}>Submit</button>
        </div>
      )}
    </div>
  );
}
