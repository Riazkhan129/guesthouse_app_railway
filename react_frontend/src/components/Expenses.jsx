import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import API from "../api";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function Expenses() {
  const { token } = useContext(AuthContext);
  const headers = { Authorization: `Bearer ${token}` };

  const [action, setAction] = useState("Add");
  const [expenses, setExpenses] = useState([]);
  const [expenseCategories, setExpenseCategories] = useState([]);
  const [expenseItems, setExpenseItems] = useState([]);
  const [selectedExpenseId, setSelectedExpenseId] = useState(null);

  const [form, setForm] = useState({
    category_id: "",
    expense_item_id: "",
    amount: "",
    notes: "",
    timestamp: new Date().toISOString(),
    date: new Date(),
  });

  const formatDateOnly = (date) => date.toISOString().split("T")[0];

  useEffect(() => {
    fetchExpenses();
    fetchExpenseCategories();
  }, []);

  useEffect(() => {
    if (form.category_id && action === "Add") fetchExpenseItems(form.category_id);
  }, [form.category_id, action]);

  const fetchExpenses = async () => {
    try {
      const res = await API.get("/expenses/", { headers });
      console.log("Fetched expenses:", res.data);
      if (res.status === 200) setExpenses(res.data);
    } catch {
      alert("❌ Failed to load expenses");
    }
  };

  const fetchExpenseCategories = async () => {
    try {
      const res = await API.get("/expense_categories/categories", { headers });
      if (res.status === 200) setExpenseCategories(res.data);
    } catch {
      alert("❌ Failed to load categories");
    }
  };

  const fetchExpenseItems = async (categoryId) => {
    try {
      const res = await API.get(`/expense_items/by_category/${categoryId}`, { headers });
      if (res.status === 200) setExpenseItems(res.data);
    } catch {
      alert("❌ Failed to load items");
    }
  };

  const resetForm = () => {
    setForm({
      category_id: "",
      expense_item_id: "",
      amount: "",
      notes: "",
      timestamp: new Date().toISOString(),
      date: new Date(),
    });
    setSelectedExpenseId(null);
  };

  const validateForm = () => {
    if (!form.category_id) return "Category is required.";
    if (!form.expense_item_id) return "Expense item is required.";
    if (!form.amount || isNaN(form.amount) || parseFloat(form.amount) <= 0) return "Amount must be positive.";
    return null;
  };

  const handleAdd = async () => {
    const error = validateForm();
    if (error) return alert("❌ " + error);
    const payload = {
      category_id: parseInt(form.category_id),
      expense_item_id: parseInt(form.expense_item_id),
      amount: parseFloat(form.amount),
      notes: form.notes || null,
      timestamp: form.timestamp,
      date: formatDateOnly(form.date),
    };
    try {
      const res = await API.post("/expenses/add", payload, { headers });
      if (res.status === 200) {
        alert("✅ Expense added");
        fetchExpenses();
        resetForm();
      }
    } catch {
      alert("❌ Failed to add expense");
    }
  };

  const handleSelectExpense = (id) => {
    const exp = expenses.find((e) => e.expense_id === parseInt(id));
    if (exp) {
      setSelectedExpenseId(exp.expense_id);
      setForm({
        category_id: exp.category_id,
        expense_item_id: exp.expense_item_id,
        amount: exp.amount,
        notes: exp.notes,
        timestamp: exp.timestamp,
        date: new Date(exp.date),
      });
    }
  };

  const handleUpdate = async () => {
    const error = validateForm();
    if (error) return alert("❌ " + error);
    const payload = {
      // category_id: parseInt(form.category_id),
      // expense_item_id: parseInt(form.expense_item_id),
      amount: parseFloat(form.amount),
      notes: form.notes || null,
      timestamp: form.timestamp,
      date: formatDateOnly(form.date),
    };
    try {
      console.log("PAYLOAD = ", payload)
      const res = await API.put(`/expenses/update/${selectedExpenseId}`, payload, { headers });
      if (res.status === 200) {
        alert("✅ Expense updated");
        fetchExpenses();
        resetForm();
      }
    } catch {
      alert("❌ Update failed");
    }
  };

  const handleDelete = async () => {
    if (!selectedExpenseId) return alert("❌ No expense selected.");
    try {
      const res = await API.delete(`/expenses/${selectedExpenseId}`, { headers });
      if (res.status === 200) {
        alert("🗑️ Expense deleted");
        fetchExpenses();
        resetForm();
      }
    } catch {
      alert("❌ Delete failed");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>📊 Expense Management</h2>

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

      {action === "Add" && (
        <div style={{ maxWidth: "800px", margin: "auto" }}>
          <FormFields
            form={form}
            setForm={setForm}
            expenseCategories={expenseCategories}
            expenseItems={expenseItems}
            mode="add"
          />
          <button onClick={handleAdd}>💾 Save</button>
        </div>
      )}

      {action === "Update" && (
        <div style={{ maxWidth: "800px", margin: "auto" }}>
          <h4>✏️ Select Expense to Update</h4>
          <select onChange={(e) => handleSelectExpense(e.target.value)} value={selectedExpenseId || ""}>
            <option value="">-- Select Expense --</option>
            {expenses.map((e) => (
              <option key={e.expense_id} value={e.expense_id}>
                {e.category_name} - {e.expense_name}
              </option>
            ))}
          </select>
          {selectedExpenseId && (
            <>
              <FormFields form={form} setForm={setForm} mode="edit" />
              <button onClick={handleUpdate}>🔁 Update</button>
            </>
          )}
        </div>
      )}

      {action === "Delete" && (
        <div style={{ maxWidth: "800px", margin: "auto" }}>
          <h4>🗑️ Select Expense to Delete</h4>
          <select onChange={(e) => handleSelectExpense(e.target.value)} value={selectedExpenseId || ""}>
            <option value="">-- Select Expense --</option>
            {expenses.map((e) => (
              <option key={e.expense_id} value={e.expense_id}>
                {e.category_name} - {e.expense_name}
              </option>
            ))}
          </select>
          {selectedExpenseId && (
            <>
              <FormFields form={form} setForm={setForm} mode="view" />
              <button onClick={handleDelete} style={{ backgroundColor: "red", color: "white" }}>
                ❌ Confirm Delete
              </button>
            </>
          )}
        </div>
      )}

      {action === "View" && (
        <div>
          <h4>📂 All Expenses</h4>
          {expenses.length === 0 ? (
            <p>No expenses found.</p>
          ) : (
            expenses.map((e) => (
              <p key={e.id}>
                📅 {e.date} | 🧾 {e.category_name} - {e.expense_name} | 💰 Rs. {e.amount} | 📝 {e.notes}
              </p>
            ))
          )}
        </div>
      )}
    </div>
  );
}

const FormFields = ({ form, setForm, expenseCategories = [], expenseItems = [], mode }) => (
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "20px" }}>
    
    {/* 🔧 Add Mode: Select category and item */}
    {mode === "add" && (
      <>
        <div>
          <label>Expense Category</label>
          <select
            value={form.category_id}
            onChange={(e) => setForm({ ...form, category_id: parseInt(e.target.value), expense_item_id: "" })}
          >
            <option value="">-- Select Category --</option>
            {expenseCategories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.category_name}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Expense Item</label>
          <select
            value={form.expense_item_id}
            onChange={(e) => setForm({ ...form, expense_item_id: parseInt(e.target.value) })}
            disabled={!form.category_id}
          >
            <option value="">-- Select Item --</option>
            {expenseItems.map((item) => (
              <option key={item.expense_item_id} value={item.expense_item_id}>
                {item.expense_name}
              </option>
            ))}
          </select>
        </div>
      </>
    )}

    {/* 🔧 Shared Fields: amount, notes, date */}
    <div>
      <label>Amount (Rs.)</label>
      <input
        type="number"
        value={form.amount}
        onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) || "" })}
        readOnly={mode === "view"}
      />
    </div>

    <div>
      <label>Notes</label>
      <input
        type="text"
        value={form.notes}
        onChange={(e) => setForm({ ...form, notes: e.target.value })}
        readOnly={mode === "view"}
      />
    </div>

    <div style={{ gridColumn: "span 2" }}>
      <label>Date</label>
      <DatePicker
        selected={form.date ? new Date(form.date) : null}
        onChange={(date) => {
          if (!date || mode === "view") return;
          const formatted = date.toISOString().split("T")[0];
          setForm((prev) => ({ ...prev, date: formatted }));
        }}
        dateFormat="dd MMM yyyy"
        className="react-datepicker-input"
        showMonthDropdown
        showYearDropdown
        dropdownMode="select"
        disabled={mode === "view"}
      />
    </div>
  </div>
);

export default Expenses;