import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

export default function ManualRepublishPage() {
  const { token } = useAuth();
  const [brands, setBrands] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedBrandId, setSelectedBrandId] = useState("");
  const [loading, setLoading] = useState(false);
  const [runProgress, setRunProgress] = useState(0);
  const [runningLabel, setRunningLabel] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  const loadBrands = () => {
    axios
      .get("/api/brands/", { headers })
      .then((res) => setBrands(res.data))
      .catch((err) => console.error(err));
  };

  const loadHistory = () => {
    axios
      .get("/api/manual/history", { headers })
      .then((res) => setHistory(res.data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    if (token) {
      loadBrands();
      loadHistory();
    }
  }, [token]);

  const startProgress = () => {
    setRunProgress(0);
    let current = 0;
    const interval = setInterval(() => {
      current = Math.min(current + 5, 90);
      setRunProgress(current);
    }, 300);
    return interval;
  };

  const stopProgress = (interval) => {
    if (interval) clearInterval(interval);
    setRunProgress(100);
    setTimeout(() => {
      setRunProgress(0);
      setRunningLabel("");
      setLoading(false);
    }, 500);
  };

  const handleRunSelected = async () => {
    if (!selectedBrandId) {
      alert("Selecciona una marca");
      return;
    }
    setLoading(true);
    setRunningLabel("Republicando marca seleccionada...");
    const interval = startProgress();
    try {
      await axios.post(
        "/api/manual/run",
        { brand_ids: [Number(selectedBrandId)], all_brands: false },
        { headers }
      );
      await loadHistory();
    } catch (err) {
      console.error(err);
      alert("Error ejecutando republicación manual");
    } finally {
      stopProgress(interval);
    }
  };

  const handleRunAll = async () => {
    if (!window.confirm("¿Republicar todas las marcas? Esto puede tardar varios minutos.")) {
      return;
    }
    setLoading(true);
    setRunningLabel("Republicando todas las marcas...");
    const interval = startProgress();
    try {
      await axios.post(
        "/api/manual/run",
        { all_brands: true },
        { headers }
      );
      await loadHistory();
    } catch (err) {
      console.error(err);
      alert("Error ejecutando republicación para todas las marcas");
    } finally {
      stopProgress(interval);
    }
  };

  return (
    <div>
      <h2>Republicación manual</h2>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3>Ejecutar republicación</h3>
        <div className="form-group">
          <label>Marca</label>
          <select
            value={selectedBrandId}
            onChange={(e) => setSelectedBrandId(e.target.value)}
          >
            <option value="">-- Selecciona una marca --</option>
            {brands.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button onClick={handleRunSelected} disabled={loading}>
            Republicar marca seleccionada
          </button>
          <button onClick={handleRunAll} disabled={loading}>
            Republicar todas las marcas
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Republicaciones manuales</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Marca</th>
              <th>Cantidad de vehículos</th>
              <th>Fecha</th>
              <th>Estatus</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h, idx) => (
              <tr key={idx}>
                <td>{h.brand_name}</td>
                <td>{h.vehicles_count}</td>
                <td>{new Date(h.run_at).toLocaleString()}</td>
                <td>{h.status}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={4}>No hay republicaciones manuales registradas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && (
        <div className="overlay">
          <div className="overlay-box">
            <h3>{runningLabel || "Ejecutando..."}</h3>
            <div
              className="progress-circle"
              style={{
                background: `conic-gradient(#2563eb ${runProgress * 3.6}deg, #e5e7eb 0deg)`,
              }}
            >
              <div className="progress-text">{runProgress}%</div>
            </div>
            <p>Por favor espera mientras se republican los vehículos.</p>
          </div>
        </div>
      )}
    </div>
  );
}
