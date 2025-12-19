
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

export default function SettingsPage() {
  const { token, user } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    username: "",
    full_name: "",
    email: "",
    role: "operator",
    password: "",
  });
  const [passwords, setPasswords] = useState({
    old_password: "",
    new_password: "",
  });

  const headers = { Authorization: `Bearer ${token}` };

  const loadUsers = () => {
    axios
      .get("/api/users/", { headers })
      .then((res) => setUsers(res.data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    if (token) {
      loadUsers();
    }
  }, [token]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        "/api/users/",
        {
          username: form.username,
          full_name: form.full_name,
          email: form.email,
          role: form.role,
          password: form.password,
        },
        { headers }
      );
      setForm({
        username: "",
        full_name: "",
        email: "",
        role: "operator",
        password: "",
      });
      loadUsers();
    } catch (err) {
      console.error(err);
      alert("Error creando usuario");
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        "/api/auth/change-password",
        null,
        {
          params: {
            old_password: passwords.old_password,
            new_password: passwords.new_password,
          },
          headers,
        }
      );
      alert("Clave actualizada");
      setPasswords({ old_password: "", new_password: "" });
    } catch (err) {
      console.error(err);
      alert("Error cambiando clave");
    }
  };

  return (
    <div>
      <h2>Configuración</h2>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3>Cambiar mi clave</h3>
        <form onSubmit={handleChangePassword}>
          <div className="form-group">
            <label>Clave actual</label>
            <input
              type="password"
              value={passwords.old_password}
              onChange={(e) =>
                setPasswords((p) => ({ ...p, old_password: e.target.value }))
              }
            />
          </div>
          <div className="form-group">
            <label>Nueva clave</label>
            <input
              type="password"
              value={passwords.new_password}
              onChange={(e) =>
                setPasswords((p) => ({ ...p, new_password: e.target.value }))
              }
            />
          </div>
          <button type="submit">Actualizar clave</button>
        </form>
      </div>

      {user?.role === "admin" || user?.is_superuser ? (
        <div className="card">
          <h3>Administrar usuarios</h3>
          <form onSubmit={handleCreate} style={{ marginBottom: "1rem" }}>
            <div className="form-group">
              <label>Usuario</label>
              <input
                value={form.username}
                onChange={(e) =>
                  setForm((f) => ({ ...f, username: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Nombre completo</label>
              <input
                value={form.full_name}
                onChange={(e) =>
                  setForm((f) => ({ ...f, full_name: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                value={form.email}
                onChange={(e) =>
                  setForm((f) => ({ ...f, email: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Rol</label>
              <select
                value={form.role}
                onChange={(e) =>
                  setForm((f) => ({ ...f, role: e.target.value }))
                }
              >
                <option value="admin">Admin</option>
                <option value="operator">Operator</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <div className="form-group">
              <label>Clave inicial</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) =>
                  setForm((f) => ({ ...f, password: e.target.value }))
                }
              />
            </div>
            <button type="submit">Crear usuario</button>
          </form>

          <ul>
            {users.map((u) => (
              <li key={u.id}>
                {u.username} ({u.role}) {u.is_active ? "" : "(inactivo)"}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>No tienes permisos para administrar otros usuarios.</p>
      )}
    </div>
  );
}
