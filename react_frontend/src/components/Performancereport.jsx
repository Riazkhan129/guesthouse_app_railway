
import React, { useEffect, useState, useContext } from "react";
import API from "../api";
import { AuthContext } from "../context/AuthContext";

const PerformanceReport = () => {
  const { token, clientId, companyName, companyLogo } = useContext(AuthContext);
  const [report, setReport] = useState(null);
  const [runtime, setRuntime] = useState("");

  useEffect(() => {
    const now = new Date();
    setRuntime(now.toLocaleString("en-GB"));
  }, []);

  useEffect(() => {
    if (!clientId || !token) return;

    API.get(`/performancereport/?client_id=${clientId}&start_date=2025-10-01&end_date=2025-10-31`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => setReport(res.data))
    .catch(err => console.error("❌ Report fetch error", err));
  }, [clientId, token]);

  if (!report) return <div>Loading report...</div>;

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "30px" }}>
        {companyLogo && (
          <img src={companyLogo} alt="Logo" style={{ maxHeight: "50px", marginRight: "12px" }} />
        )}
        <h2 style={{ margin: 0 }}>🏨 {companyName}</h2>
      </div>

      <div style={{ textAlign: "right", marginBottom: "20px" }}>{runtime}</div>

      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "30px" }}>
        <tbody>
          <tr><td><strong>Total Rooms</strong></td><td>{report.total_rooms}</td></tr>
          <tr><td><strong>Occupied Rooms</strong></td><td>{report.occupied_rooms}</td></tr>
          <tr><td><strong>Vacant Rooms</strong></td><td>{report.vacant_rooms}</td></tr>
          <tr><td><strong>Occupancy Rate</strong></td><td>{report.occupancy_rate}%</td></tr>
          <tr><td><strong>Total Revenue</strong></td><td>Rs. {report.total_revenue.toLocaleString()}</td></tr>
          <tr><td><strong>Total Expenses</strong></td><td>Rs. {report.total_expenses.toLocaleString()}</td></tr>
          <tr><td><strong>Profit</strong></td><td>Rs. {report.profit.toLocaleString()}</td></tr>
        </tbody>
      </table>

      <h3>🌍 Guest Nationality Breakdown</h3>
      <ul>
        {report.demographics.map(([nation, count], i) => (
          <li key={i}>{nation}: {count}</li>
        ))}
      </ul>

      <button onClick={() => window.print()} style={{ marginTop: "20px" }}>
        🖨️ Print / Export PDF
      </button>
    </div>
  );
};

export default PerformanceReport;
