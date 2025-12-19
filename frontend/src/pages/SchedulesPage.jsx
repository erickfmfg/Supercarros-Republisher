import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

// MUI + Dayjs
import dayjs from "dayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { TimePicker } from "@mui/x-date-pickers/TimePicker";

const DAY_OPTIONS = [
  { value: "mon", label: "L" },
  { value: "tue", label: "M" },
  { value: "wed", label: "X" },
  { value: "thu", label: "J" },
  { value: "fri", label: "V" },
  { value: "sat", label: "S" },
  { value: "sun", label: "D" },
];

const dayLabelFromValue = (value) => {
  const map = {
    mon: "Lunes",
    tue: "Martes",
    wed: "Miércoles",
    thu: "Jueves",
    fri: "Viernes",
    sat: "Sábado",
    sun: "Domingo",
  };
  return map[value] || value;
};

// Componente de selección de días tipo "chips"
function DaySelector({ value, onChange }) {
  const toggleDay = (d) => {
    if (value.includes(d)) {
      onChange(value.filter((x) => x !== d));
    } else {
      onChange([...value, d]);
    }
  };

  return (
    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
      {DAY_OPTIONS.map((d) => (
        <button
          key={d.value}
          type="button"
          onClick={() => toggleDay(d.value)}
          className={`day-chip ${
            value.includes(d.value) ? "day-chip-active" : ""
          }`}
        >
          {d.label}
        </button>
      ))}
    </div>
  );
}

export default function SchedulesPage() {
  const { token } = useAuth();
  const [brands, setBrands] = useState([]);
  const [schedules, setSchedules] = useState([]);

  const [name, setName] = useState("");
  const [selectedBrandIds, setSelectedBrandIds] = useState([]);
  const [daysOfWeek, setDaysOfWeek] = useState([]);

  // timeInput ahora es un objeto dayjs
  const [timeInput, setTimeInput] = useState(() =>
    dayjs().hour(9).minute(0).second(0)
  );
  // timesOfDay sigue siendo array de strings "HH:mm" para el backend
  const [timesOfDay, setTimesOfDay] = useState(["09:00"]);

  const [brandFilter, setBrandFilter] = useState("");

  const [runningScheduleId, setRunningScheduleId] = useState(null);
  const [runProgress, setRunProgress] = useState(0);

  const headers = { Authorization: `Bearer ${token}` };

  const loadData = () => {
    axios.get("/api/brands/", { headers }).then((res) => setBrands(res.data));
    axios.get("/api/schedules/", { headers }).then((res) => setSchedules(res.data));
  };

  useEffect(() => {
    if (token) loadData();
  }, [token]);

  const toggleBrand = (id) => {
    setSelectedBrandIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const addTime = () => {
    if (!timeInput) return;
    // convertimos el dayjs actual a string "HH:mm" para el backend
    const tStr = timeInput.format("HH:mm");
    if (!timesOfDay.includes(tStr)) {
      setTimesOfDay((prev) => [...prev, tStr]);
    }
  };

  const removeTime = (t) => {
    setTimesOfDay((prev) => prev.filter((x) => x !== t));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!name) {
      alert("El nombre es requerido");
      return;
    }
    if (daysOfWeek.length === 0) {
      alert("Debes seleccionar al menos un día");
      return;
    }
    if (timesOfDay.length === 0) {
      alert("Debes agregar al menos una hora");
      return;
    }
    if (selectedBrandIds.length === 0) {
      alert("Debes seleccionar al menos una marca");
      return;
    }

    try {
      await axios.post(
        "/api/schedules/",
        {
          name,
          is_active: true,
          interval_minutes: null,
          brand_ids: selectedBrandIds,
          days_of_week: daysOfWeek.join(","),
          times_of_day: timesOfDay.join(","), // backend sigue recibiendo "HH:mm,HH:mm"
        },
        { headers }
      );
      setName("");
      setSelectedBrandIds([]);
      setDaysOfWeek([]);
      setTimeInput(dayjs().hour(9).minute(0).second(0));
      setTimesOfDay(["09:00"]);
      loadData();
    } catch (err) {
      console.error(err);
      alert(
        err.response?.data?.detail ||
          "Error creando programación (verifica los datos)"
      );
    }
  };

  const handlePause = async (id) => {
    await axios.post(`/api/schedules/${id}/pause`, null, { headers });
    loadData();
  };

  const handleResume = async (id) => {
    await axios.post(`/api/schedules/${id}/resume`, null, { headers });
    loadData();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Eliminar esta programación?")) return;
    await axios.delete(`/api/schedules/${id}`, { headers });
    loadData();
  };

  const handleRunOnce = async (id) => {
    setRunningScheduleId(id);
    setRunProgress(0);
    let current = 0;
    const interval = setInterval(() => {
      current = Math.min(current + 5, 90);
      setRunProgress(current);
    }, 300);

    try {
      await axios.post(`/api/schedules/${id}/run-once`, null, { headers });
      setRunProgress(100);
      await new Promise((resolve) => setTimeout(resolve, 500));
    } catch (err) {
      console.error(err);
      alert("Error ejecutando la programación");
    } finally {
      clearInterval(interval);
      setRunningScheduleId(null);
      setRunProgress(0);
      loadData();
    }
  };

  const filteredBrands = brands.filter((b) =>
    b.name.toLowerCase().includes(brandFilter.toLowerCase())
  );

  return (
    <div>
      <h2>Programar republicación</h2>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3>Nueva programación</h3>
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label>Nombre</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>

          <div className="form-group">
            <label>Días de la semana</label>
            <DaySelector value={daysOfWeek} onChange={setDaysOfWeek} />
          </div>

          <div className="form-group">
            {/*<label>Horas de ejecución</label>*/}
            <div className="time-picker-row">
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <TimePicker
                  label="Hora"
                  ampm // muestra AM/PM como en tu ejemplo
                  value={timeInput}
                  onChange={(newValue) => {
                    if (newValue) {
                      setTimeInput(newValue);
                    }
                  }}
                  slotProps={{
                    textField: {
                      size: "small",
                    },
                  }}
                />
              </LocalizationProvider>
              <button type="button" onClick={addTime}>
                Agregar hora
              </button>
            </div>

            <div className="time-tags-row">
              {timesOfDay.map((t) => (
                <div key={t} className="time-chip">
                  <span>{t}</span>
                  <button
                    type="button"
                    onClick={() => removeTime(t)}
                    className="time-chip-remove"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Filtrar marcas</label>
            <input
              placeholder="Escribe para filtrar..."
              value={brandFilter}
              onChange={(e) => setBrandFilter(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Marcas</label>
            <div
              style={{
                maxHeight: 150,
                overflowY: "auto",
                border: "1px solid #e5e7eb",
                padding: "0.5rem",
              }}
            >
              {filteredBrands.map((b) => (
                <label
                  key={b.id}
                  style={{ display: "block", fontSize: "0.875rem" }}
                >
                  <input
                    type="checkbox"
                    checked={selectedBrandIds.includes(b.id)}
                    onChange={() => toggleBrand(b.id)}
                  />{" "}
                  {b.name}
                </label>
              ))}
              {filteredBrands.length === 0 && (
                <div style={{ fontSize: "0.875rem" }}>
                  No hay marcas que coincidan.
                </div>
              )}
            </div>
          </div>
          <button type="submit">Crear programación</button>
        </form>
      </div>

      <div className="card">
        <h3>Programaciones existentes</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Días</th>
              <th>Horas</th>
              <th>Activa</th>
              <th>Marcas</th>
              <th>Última ejecución</th>
              <th>Próxima ejecución</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {schedules.map((s) => {
              const daysStr = (s.days_of_week || "")
                .split(",")
                .filter(Boolean)
                .map((d) => dayLabelFromValue(d))
                .join(", ");
              const timesStr = (s.times_of_day || "")
                .split(",")
                .filter(Boolean)
                .join(", ");
              const brandsStr = (s.brands || []).map((b) => b.name).join(", ");
              return (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{daysStr || "-"}</td>
                  <td>{timesStr || "-"}</td>
                  <td>{s.is_active ? "Sí" : "No"}</td>
                  <td>{brandsStr || "-"}</td>
                  <td>
                    {s.last_run_at
                      ? new Date(s.last_run_at).toLocaleString()
                      : "-"}
                  </td>
                  <td>
                    {s.next_run_at
                      ? new Date(s.next_run_at).toLocaleString()
                      : "-"}
                  </td>
                  <td>
                    <button
                      onClick={() => handleRunOnce(s.id)}
                      disabled={runningScheduleId === s.id}
                    >
                      Ejecutar ahora
                    </button>{" "}
                    {s.is_active ? (
                      <button onClick={() => handlePause(s.id)}>Pausar</button>
                    ) : (
                      <button onClick={() => handleResume(s.id)}>
                        Reanudar
                      </button>
                    )}{" "}
                    <button onClick={() => handleDelete(s.id)}>Eliminar</button>
                  </td>
                </tr>
              );
            })}
            {schedules.length === 0 && (
              <tr>
                <td colSpan={8}>No hay programaciones creadas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {runningScheduleId && (
        <div className="overlay">
          <div className="overlay-box">
            <h3>Ejecutando programación...</h3>
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
