import { useEffect, useState, useContext } from "react";
// import React, { useEffect, useState, usecontext } from "react";
import API from "../api"; // ✅ ADDED: Centralized Axios instance
import { AuthContext } from "../context/AuthContext"; // ✅ ADDED: For token
import dayjs from "dayjs";

const Dashboard = () => {
  const { token } = useContext(AuthContext); // ✅ ADDED: Get token from context
  const [dashboardData, setDashboardData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await API.get("dashboard/monthly", {
        headers: { Authorization: `Bearer ${token}` } // ✅ CHANGED
      });
      const sortedData = response.data.sort(
        (a, b) => new Date(b.month) - new Date(a.month)
      );

      const allCats = new Set();
      sortedData.forEach(row => {
        Object.keys(row.expenses || {}).forEach(cat => allCats.add(cat));
      });

      setCategories(Array.from(allCats));
      setDashboardData(sortedData);
    } catch (err) {
      setError("Failed to load dashboard data");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "16px" }}>
        Guest House Dashboard
      </h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Summary */}
      <h3 style={{ fontSize: "16px", fontWeight: "bold", marginTop: "24px", marginBottom: "12px" }}>
        Monthly Summary
      </h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", fontWeight: "bold", background: "#f0f0f0", padding: "10px" }}>
        <div>Month</div>
        <div>Income</div>
        <div>Expenses</div>
        <div>Profit/Loss</div>
        <div>Pending</div>
      </div>

      {dashboardData.map((row, idx) => {
        // const income = row.room_charges || 0;
        const income = row.total_income || 0;
        
        const expenses = categories.reduce(
          (sum, cat) => sum + (row.expenses?.[cat] || 0),
          0
        );
        const profit = row.profit_loss || 0;
        const pending = row.pending_bookings || 0;

        return (
          <div key={idx} style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, 1fr)",
            borderBottom: "1px solid #ccc",
            padding: "10px 0"
          }}>
            <div>{dayjs(row.month).format("MMM YYYY")}</div>
            <div>Rs. {income.toLocaleString()}</div>
            <div>Rs. {expenses.toLocaleString()}</div>
            <div style={{ color: profit >= 0 ? "green" : "red" }}>
              Rs. {profit.toLocaleString()}
            </div>
            <div>{pending}</div>
          </div>
        );
      })}

      {/* Expenses */}
      <h3 style={{ fontSize: "16px", fontWeight: "bold", marginTop: "24px", marginBottom: "12px" }}>
        Monthly Expenses by Category
      </h3>

      {/* Header */}
      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(${categories.length + 1}, 1fr)`,
        fontWeight: "bold",
        background: "#f0f0f0",
        padding: "10px"
      }}>
        <div>Month</div>
        {categories.map((cat, idx) => (
          <div key={idx}>{cat}</div>
        ))}
      </div>

      {/* Rows */}
      {dashboardData.map((row, idx) => (
        <div
          key={idx}
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${categories.length + 1}, 1fr)`,
            borderBottom: "1px solid #ccc",
            padding: "10px 0"
          }}
        >
          <div>{dayjs(row.month).format("MMM YYYY")}</div>
          {categories.map((cat, j) => (
            <div key={j} style={{ textAlign: "center" }}>
              Rs. {(row.expenses?.[cat] || 0).toLocaleString()}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default Dashboard;
