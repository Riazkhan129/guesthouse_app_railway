import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

export default function ExpenseItems() {
  const { token } = useContext(AuthContext);
  const [mode, setMode] = useState("add");
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState({
    category_id: "",
    expense_name: "",
    default_price: "",
    unit: "",
    is_activated: true
  });

  const fetchItems = () => {
    API.get("/expenseitems/expense_categories/items", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setItems(res.data));
  };

  const fetchCategories = () => {
    API.get("/expensecategories/categories", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setCategories(res.data));
  };

  useEffect(() => {
    fetchItems();
    fetchCategories();
  }, []);

  useEffect(() => {
    if (mode !== "add") {
      const selected = items.find(i => i.expense_item_id === parseInt(selectedId));
      if (selected) {
        setForm({
          category_id: selected.category_id,
          expense_name: selected.expense_name,
          default_price: selected.default_price,
          unit: selected.unit,
          is_activated: selected.is_activated
        });
      }
    } else {
      setForm({
        category_id: "",
        expense_name: "",
        default_price: "",
        unit: "",
        is_activated: true
      });
      setSelectedId("");
    }
  }, [selectedId, mode]);

  const getCategoryName = (id) => {
    const cat = categories.find(c => c.id === id);
    return cat ? cat.category_name : "Unknown";
  };

  const handleSubmit = async () => {
    let res;
    if (mode === "add") {
      res = await API.post("/expenseitems/expense_categories/items", form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("✅ Expense item added");
      // ✅ Reset form to blank
      setForm({
        category_id: "",
        expense_name: "",
        default_price: "",
        unit: "",
        is_activated: true
      });
    } else if (mode === "update") {
      res = await API.put(`/expenseitems/expense_categories/items/${selectedId}`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("✏️ Expense item updated");
    } else if (mode === "delete") {
      res = await API.delete(`/expenseitems/expense_categories/items/${selectedId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("🗑️ Expense item deleted");
    }
    fetchItems();
    setSelectedId("");
  };

  return (
    <div>
      <h3>🧾 Expense Items</h3>

      {/* 🔹 Mode buttons */}
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

      {/* 🔹 ADD */}
      {mode === "add" && (
      <>
        <div style={{ display: "flex", gap: "100px", marginBottom: "12px" }}>
          <label>
            Category : 
            <select
              value={form.category_id}
              onChange={e => setForm({ ...form, category_id: parseInt(e.target.value) })}
              style={{ width: "280px" }}
            >
              <option value="">-- Select Category --</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.category_name}</option>
              ))}
            </select>
          </label>

          <label>
            Item : 
            <input
              type="text"
              value={form.expense_name}
              onChange={e => setForm({ ...form, expense_name: e.target.value })}
              style={{ width: "280px" }}
            />
          </label>
        </div>
        
        {/* 🔹 Line 2: Default Price + Unit + Active */}
        <div style={{ display: "flex", gap: "200px", marginBottom: "12px", alignItems: "center" }}>
          <label>
            Price :
            <input
              type="number"
              value={form.default_price}
              onChange={e => setForm({ ...form, default_price: parseFloat(e.target.value) })}
              style={{ width: "120px", marginLeft: "25px" }}
            />
          </label>

          <label>
            Unit :
            <input
              type="text"
              value={form.unit}
              onChange={e => setForm({ ...form, unit: e.target.value })}
              style={{ width: "120px" }}
            />
          </label>

          <label style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span>Status</span>
            <select
              value={form.is_activated ? "true" : "false"}
              onChange={e => setForm({ ...form, is_activated: e.target.value === "true" })}
              style={{ width: "140px" }}
            >
              <option value="true">Active</option>
              <option value="false">Non-Active</option>
            </select>
          </label>
        </div>

        {/* ✅ 🔧 Submit button moved outside flex container */}
        <div style={{ textAlign: "center", marginTop: "12px" }}>
          <button onClick={handleSubmit}>Submit</button>
        </div>
      </>
      )}

      {/* 🔹 UPDATE */}
      {mode === "update" && (
        <>
          {/* 🔹 Dropdown to select item */}
          <select
            value={selectedId}
            onChange={e => setSelectedId(e.target.value)}
            style={{ width: "280px", marginBottom: "12px" }}
          >
            <option value="">Select Item</option>
            {items.map(i => (
              <option key={i.expense_item_id} value={i.expense_item_id}>
                {getCategoryName(i.category_id)} — {i.expense_name}
              </option>
            ))}
          </select>

          {selectedId && (
            <>
              {/* 🔹 Line 1: Category + Expense Name */}
              <div style={{ display: "flex", gap: "100px", marginBottom: "12px" }}>
                <label>
                  Category :
                  <input
                    type="text"
                    value={getCategoryName(form.category_id)}
                    disabled
                    style={{ width: "280px", marginLeft: "12px" }}
                  />
                </label>

                <label>
                  Item :
                  <input
                    type="text"
                    value={form.expense_name}
                    disabled
                    style={{ width: "280px", marginLeft: "12px" }}
                  />
                </label>
              </div>

              {/* 🔹 Line 2: Default Price + Unit + Active */}
              <div style={{ display: "flex", gap: "100px", marginBottom: "12px", alignItems: "center" }}>
                <label>
                  Price :
                  <input
                    type="number"
                    value={form.default_price}
                    onChange={e => setForm({ ...form, default_price: parseFloat(e.target.value) })}
                    style={{ width: "120px", marginLeft: "25px" }}
                  />
                </label>

                <label>
                  Unit :
                  <input
                    type="text"
                    value={form.unit}
                    onChange={e => setForm({ ...form, unit: e.target.value })}
                    style={{ width: "120px", marginLeft: "12px" }}
                  />
                </label>

                {/* ✅ Replaced checkbox with dropdown */}
                <label style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <span>Active</span>
                  <select
                    value={form.is_activated ? "true" : "false"}
                    onChange={e => setForm({ ...form, is_activated: e.target.value === "true" })}
                    style={{ width: "140px" }}
                  >
                    <option value="true">Active</option>
                    <option value="false">Non-Active</option>
                  </select>
                </label>
              </div>

              {/* ✅ Submit button on new centered line */}
              <div style={{ textAlign: "center", marginTop: "12px" }}>
                <button onClick={handleSubmit}>Submit</button>
              </div>
            </>
          )}
        </>
      )}

      {/* 🔹 DELETE */}
      {mode === "delete" && (
        <>
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ width: "280px" }}>
            <option value="">Select Item</option>
            {items.map(i => (
              <option key={i.expense_item_id} value={i.expense_item_id}>
                {getCategoryName(i.category_id)} — {i.expense_name}
              </option>
            ))}
          </select>

          {selectedId && (
            <div style={{ marginTop: "12px" }}>
              <p><strong>Category:</strong> {getCategoryName(form.category_id)}</p>
              <p><strong>Expense Name:</strong> {form.expense_name}</p>
              <p><strong>Default Price:</strong> {form.default_price}</p>
              <p><strong>Unit:</strong> {form.unit}</p>
              <p><strong>Active:</strong> {form.is_activated ? "Yes" : "No"}</p>
              <br /><br />
              <button onClick={handleSubmit}>Submit</button>
            </div>
          )}
        </>
      )}

     {/* 🔹 VIEW */}
{mode === "view" && (
  <div style={{ marginTop: "12px" }}>
    <ul style={{ listStyle: "none", paddingLeft: 0 }}>
      {items.map(i => (
        <li key={i.expense_item_id} style={{ marginBottom: "8px", borderBottom: "1px solid #ccc", paddingBottom: "6px" }}>
          <strong>Category:</strong> {getCategoryName(i.category_id)}<br />
          <strong>Expense Name:</strong> {i.expense_name}<br />
          <strong>Default Price:</strong> {i.default_price}<br />
          <strong>Unit:</strong> {i.unit}<br />
          <strong>Active:</strong> {i.is_activated ? "Yes" : "No"}<br />
          {/* <strong>Created:</strong> {i.created}*/}
        </li>
      ))}
    </ul>
  </div>
)}
  </div>
)}
