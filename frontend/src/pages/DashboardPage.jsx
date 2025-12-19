
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const { token } = useAuth();
  const [stats, setStats] = useState([]);

  useEffect(() => {
    if (!token) return;
    axios
      .get("/api/stats/brands/last-month", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setStats(res.data))
      .catch((err) => console.error(err));
  }, [token]);

  // Agrupar por marca
  const grouped = stats.reduce((acc, item) => {
    const key = item.brand_name;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});

  return (
    <div>
      <h2>Resumen último mes</h2>
      <div className="card-grid">
        {Object.keys(grouped).length === 0 && (
          <p>No hay datos de republicaciones aún.</p>
        )}
        {Object.entries(grouped).map(([brand, items]) => {
          const total = items.reduce(
            (sum, it) => sum + it.vehicles_count,
            0
          );
          return (
            <div className="card" key={brand}>
              <h3>{brand}</h3>
              <p>Total republicados (último mes): {total}</p>
              <ul style={{ maxHeight: 150, overflowY: "auto", fontSize: "0.875rem" }}>
                {items.map((it, idx) => (
                  <li key={idx}>
                    {new Date(it.date).toLocaleDateString()}: {it.vehicles_count}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
