import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
// 🔧 UPDATED: Add datepicker import
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";


function Expenses() {
  const { token } = useContext(AuthContext);
  const API_URL = "http://localhost:8000";

  const [action, setAction] = useState("Add");
  const [expenses, setExpenses] = useState([]);
  const formatDateOnly = (date) => date.toISOString().split("T")[0];
  
  
  
  const [form, setForm] = useState({
    title: "",
    amount: "",
    category: "Electric",
    notes: "",
    timestamp:new Date().toISOString(),
    date: new Date(),
  });

  const [filterDates, setFilterDates] = useState({
  start: formatDateOnly(new Date(new Date().setDate(new Date().getDate() - 30))),
  end: formatDateOnly(new Date()),
});

  const [categoryFilter, setCategoryFilter] = useState("All");
  const [selectedExpenseId, setSelectedExpenseId] = useState(null);

  const categories = ["Electric", "Gas", "Rent", "Salary", "Laundry", "Misc"];
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const res = await axios.get(`${API_URL}/expenses/`, { headers });
      if (res.status === 200) setExpenses(res.data);
    } catch (err) {
      alert("❌ Failed to load expenses");
    }
  };

  const resetForm = () => {
    setForm({
      title: "",
      amount: "",
      category: "Electric",
      notes: "",
      date: new Date().toISOString().split("T")[0],
    });
    setSelectedExpenseId(null);
  };

  const validateForm = () => {
    if (!form.title.trim()) return "Title is required.";
    if (form.amount === "" || isNaN(form.amount) || parseFloat(form.amount) <= 0)
      return "Amount must be a positive number.";
    if (!form.date) return "Date is required.";
    return null;
  };

  const handleAdd = async () => {
    const error = validateForm();
    if (error) return alert("❌ " + error);
    console.log("Sending to backend:", form);
    console.log("Type of form.date:", typeof form.date);

    try {
      const res = await axios.post(`${API_URL}/expenses/add`, form, { headers });
      if (res.status === 200) {
        alert("✅ Expense added");
        fetchExpenses();
        resetForm();
      }
    } catch (err) {
      alert("❌ Failed to add expense");
    }
  };

  const handleUpdate = async () => {
    const error = validateForm();
    if (error) return alert("❌ " + error);

    try {
      const res = await axios.put(`${API_URL}/expenses/update/${selectedExpenseId}`, form, { headers });
      if (res.status === 200) {
        alert("✅ Expense updated");
        fetchExpenses();
        resetForm();
      }
    } catch (err) {
      alert("❌ Update failed");
    }
  };

  const handleDelete = async () => {
    if (!selectedExpenseId) return alert("❌ No expense selected.");

    try {
      const res = await axios.delete(`${API_URL}/expenses/${selectedExpenseId}`, { headers });
      if (res.status === 200) {
        alert("🗑️ Expense deleted");
        fetchExpenses();
        resetForm();
      }
    } catch (err) {
      alert("❌ Delete failed");
    }
  };

  const handleSelectExpense = (id) => {
    const exp = expenses.find((e) => e.id === parseInt(id));
    if (exp) {
      setSelectedExpenseId(exp.id);
      setForm({ ...exp, amount: parseFloat(exp.amount) });
    }
  };

  const getFilteredExpenses = () => {
    return expenses.filter((e) => {
      const d = new Date(e.date);
      const start = filterDates.start;
      const end = filterDates.end;

      return (
        d >= start &&
        d <= end &&
        (categoryFilter === "All" || e.category === categoryFilter)
      );
    });
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>📊 Expense Management</h2>

      {/* Action Buttons */}
      <div style={{ marginBottom: "10px" }}>
        {["Add", "Update", "Delete", "View"].map((opt) => (
          <button
            key={opt}
            onClick={() => {
              setAction(opt);
              resetForm();
            }}
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              background: action === opt ? "#4CAF50" : "#eee",
              border: "1px solid #ccc",
              cursor: "pointer",
            }}
          >
            {opt}
          </button>
        ))}
      </div>

      <hr />

      {/* Add */}
      {action === "Add" && (
        <div style={{ maxWidth: "800px", margin: "auto" }}>
          <h4>➕ Add Expense</h4>
          <FormFields form={form} setForm={setForm} categories={categories} />
          <button onClick={handleAdd}>💾 Save</button>
        </div>
      )}

      {/* Update */}
      {action === "Update" && (
        <div>
          <h4>✏️ Update Expense</h4>
          <Filters
            categoryFilter={categoryFilter}
            setCategoryFilter={setCategoryFilter}
            filterDates={filterDates}
            setFilterDates={setFilterDates}
            categories={categories}
          />
          <select
            onChange={(e) => handleSelectExpense(e.target.value)}
            value={selectedExpenseId || ""}
          >
            <option value="">-- Select Expense --</option>
            {getFilteredExpenses().map((e) => (
              <option key={e.id} value={e.id}>
                {e.id} - {e.category} ({e.date}) - Rs. {e.amount}
              </option>
            ))}
          </select>
          {selectedExpenseId && (
            <>
              <FormFields form={form} setForm={setForm} categories={categories} />
              <button onClick={handleUpdate}>🔁 Update</button>
            </>
          )}
        </div>
      )}

      {/* Delete */}
      {action === "Delete" && (
        <div>
          <h4>🗑️ Delete Expense</h4>
          <select
            onChange={(e) => handleSelectExpense(e.target.value)}
            value={selectedExpenseId || ""}
          >
            <option value="">-- Select Expense --</option>
            {expenses.map((e) => (
              <option key={e.id} value={e.id}>
                {e.id} - {e.category} ({e.date})
              </option>
            ))}
          </select>

          {selectedExpenseId && (() => {
            const selected = expenses.find((e) => e.id === selectedExpenseId);
            if (!selected) return null;
            return (
              <div style={{ marginTop: "1rem", border: "1px solid #ccc", padding: "10px" }}>
                <p><strong>Title:</strong> {selected.title}</p>
                <p><strong>Amount:</strong> Rs. {selected.amount}</p>
                <p><strong>Category:</strong> {selected.category}</p>
                <p><strong>Date:</strong> {selected.date}</p>
                {selected.notes && <p><strong>Notes:</strong> {selected.notes}</p>}
                <button onClick={handleDelete} style={{ backgroundColor: "red", color: "white" }}>
                  ❌ Confirm Delete
                </button>
              </div>
            );
          })()}
        </div>
      )}

      {/* View */}
      {action === "View" && (
        <div>
          <h4>📂 View Expenses</h4>
          <Filters
            categoryFilter={categoryFilter}
            setCategoryFilter={setCategoryFilter}
            filterDates={filterDates}
            setFilterDates={setFilterDates}
            categories={categories}
          />
          {getFilteredExpenses().length === 0 ? (
            <p>No expenses found in selected range.</p>
          ) : (
            getFilteredExpenses().map((e) => (
              <p key={e.id}>
                📅 <strong>{e.date}</strong> | 💼 <strong>{e.category}</strong>:
                Rs. <strong>{e.amount}</strong> - <em>{e.notes}</em>
              </p>
            ))
          )}
        </div>
      )}
    </div>
  );
}

const FormFields = ({ form, setForm, categories }) => (
  <>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
      <div>
        <label>Title</label>
        <input
          type="text"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />
      </div>
      <div>
        <label>Amount (Rs.)</label>
        <input
          type="number"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) || "" })}
        />
      </div>
      <div>
        <label>Category</label>
        <select
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        >
          {categories.map((cat) => (
            <option key={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div style={{ display: "flex", flexDirection: "column", marginBottom: "1rem" }}>
        <label style={{ marginBottom: "5px" }}>Date</label>
        {/* 🔧 UPDATED: Use react-datepicker */}
        <DatePicker
          selected={form.date ? new Date(form.date) : null}
          onChange={(date) => {
            if (!date) return;
            const formatted = date.toISOString().split("T")[0]; // ✅ "YYYY-MM-DD"
            setForm((prev) => ({ ...prev, date: formatted }));
          }}
          dateFormat="dd MMM yyyy"
          className="react-datepicker-input"
          showMonthDropdown
          showYearDropdown
          dropdownMode="select"
        />
      </div>

    </div>
    <div>
      <label>Notes</label>
      <textarea
        value={form.notes}
        onChange={(e) => setForm({ ...form, notes: e.target.value })}
        style={{ width: "100%", marginTop: "10px" }}
      />
    </div>
  </>
);

const Filters = ({ categoryFilter, setCategoryFilter, filterDates, setFilterDates, categories }) => (
  <div style={{ marginBottom: "1rem" }}>
    <label>Category Filter:</label>
    <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
      <option>All</option>
      {categories.map((cat) => (
        <option key={cat}>{cat}</option>
      ))}
    </select>
    <div style={{ display: "flex", gap: "2rem", marginTop: "0.5rem" }}>
    <div style={{ display: "flex", flexDirection: "column" }}> {/* 🔧 UPDATED */}
      <label style={{ display: "block", marginBottom: "5px" }}>Start Date</label> {/* 🔧 UPDATED */}
        <DatePicker
          selected={filterDates.start}
          onChange={(date) => setFilterDates({ ...filterDates, start: date })}
          dateFormat="dd MMM yyyy"
          className="react-datepicker-input"
        />

      </div>
      <div style={{ display: "flex", flexDirection: "column" }}> {/* 🔧 UPDATED */}
      <label style={{ display: "block", marginBottom: "5px" }}>End Date</label> {/* 🔧 UPDATED */}
        <DatePicker
          selected={filterDates.end}
          onChange={(date) => setFilterDates({ ...filterDates, end: date })}
          dateFormat="dd MMM yyyy"
          className="react-datepicker-input"
        />

      </div>
    </div>
  </div>
);

export default Expenses;
