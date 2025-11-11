import React, { useEffect, useState, useContext, useRef } from "react"; // 🔹 Added useRef for auto-focus
import API from "../api";
import { AuthContext } from "../context/AuthContext";

export default function ExpenseCategories() {
  const { token } = useContext(AuthContext);
  const [mode, setMode] = useState("add");
  const [categories, setCategories] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState({ category_name: "", category_active: true });
  const [error, setError] = useState(""); // 🔹 Added for inline validation
  const inputRef = useRef(null); // 🔹 For auto-focus

  useEffect(() => {
    API.get("/expensecategories/categories", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setCategories(res.data));
  }, []);

  useEffect(() => {
    if (mode === "add") {
      setForm({ category_name: "", category_active: true }); // 🔹 Reset form in Add mode
      setSelectedId("");
      setError("");
      setTimeout(() => inputRef.current?.focus(), 100); // 🔹 Auto-focus input
    } else if (mode !== "view") {
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

  const fetchCategories = () => {
    API.get("/expensecategories/categories", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setCategories(res.data));
  };

  useEffect(() => {
    fetchCategories(); // 🔹 Initial fetch
  }, []);

  const handleSubmit = async () => {
    if (!form.category_name.trim()) {
      setError("Category name is required."); // 🔹 Inline validation
      return;
    }

    let res;
    if (mode === "add") {
      res = await API.post("/expensecategories/categories", form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchCategories(); // 🔹 Refresh list
      setSelectedId(""); // 🔹 Reset selection
      alert("✅ Category added successfully!");
    } else if (mode === "update") {
      res = await API.put(`/expensecategories/categories/${selectedId}`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchCategories(); // 🔹 Refresh list
      alert("✏️ Category updated successfully!");
    } else if (mode === "delete") {
      res = await API.delete(`/expensecategories/categories/${selectedId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchCategories(); // 🔹 Refresh list
      setSelectedId(""); // 🔹 Reset selection
      alert("🗑️ Category deleted successfully!");
    }
    // alert(res?.data?.message || "Category complete");
  };

  return (
    <div>
      <h3>📂 Expense Categories</h3>

      {/* 🔹 Highlight selected mode button */}
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

      {/* 🔹 Hide dropdown in view mode */}
      {(mode !== "add" && mode !== "view") && (
        <select value={selectedId} onChange={e => setSelectedId(e.target.value)}
          style={{ width: "220px" }}
        >
          <option value="">Select Category</option>
          {categories.map(c => (
            <option key={c.id} value={c.id}>{c.category_name}</option>
          ))}
        </select>
      )}

      {/* 🔹 Add/Edit form with inline layout, toggle switch, and readonly input in update */}
      {(mode === "add" || mode === "update") && (
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "12px" }}>
          <label>Category</label>
          <input
            ref={inputRef}
            type="text"
            placeholder="Enter category name"
            value={form.category_name}
            onChange={e => setForm({ ...form, category_name: e.target.value })}
            disabled={mode === "update"} // 🔹 Readonly in update mode
            style={{ borderColor: error ? "red" : "#ccc",
             width: "min(220px, 100%)"}}
          />
          {/* ✅ 🔄 Replaced toggle with dropdown */}
          <label style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span>Status</span>
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

      {/* 🔹 Inline validation error */}
      {error && <p style={{ color: "red", marginTop: "4px" }}>{error}</p>}

      {/* 🔹 View mode shows all categories with spacing */}
      {mode === "view" && (
        <div>
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

      {mode !== "view" && (
        <div style={{ textAlign: "left", marginTop: "16px", marginLeft: "250px" }}>
          <button onClick={handleSubmit}>Submit</button>
        </div>
      )}

  
      {/* 🔹 Toggle switch styles */}
      <style>{`
        .switch {
          position: relative;
          display: inline-block;
          width: 40px;
          height: 20px;
        }
        .switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        .slider {
          position: absolute;
          cursor: pointer;
          top: 0; left: 0;
          right: 0; bottom: 0;
          background-color: #ccc;
          transition: .4s;
          border-radius: 20px;
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 14px;
          width: 14px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: .4s;
          border-radius: 50%;
        }
        input:checked + .slider {
          background-color: #007bff;
        }
        input:checked + .slider:before {
          transform: translateX(20px);
        }
      `}</style>
    </div>
  );
}

