import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

export default function BrandsPage() {
  const { token } = useAuth();
  const [brands, setBrands] = useState([]);
  const [newBrand, setNewBrand] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  const loadBrands = () => {
    axios
      .get("/api/brands/", { headers })
      .then((res) => setBrands(res.data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    if (token) {
      loadBrands();
    }
  }, [token]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newBrand) return;
    try {
      await axios.post(
        "/api/brands/",
        { name: newBrand, is_active: true },
        { headers }
      );
      setNewBrand("");
      loadBrands();
    } catch (err) {
      console.error(err);
      alert("Error creando marca");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Eliminar esta marca?")) return;
    try {
      await axios.delete(`/api/brands/${id}`, { headers });
      loadBrands();
    } catch (err) {
      console.error(err);
      alert("Error eliminando marca");
    }
  };

  return (
    <div>
      <h2>Marcas</h2>
      <form onSubmit={handleAdd} style={{ marginBottom: "1rem" }}>
        <div className="form-group">
          <label>Nueva marca</label>
          <input
            value={newBrand}
            onChange={(e) => setNewBrand(e.target.value)}
            placeholder="Ej: Lexus"
          />
        </div>
        <button type="submit">Agregar</button>
      </form>

      <div className="card">
        <h3>Listado de marcas</h3>
        <ul>
          {brands.map((b) => (
            <li
              key={b.id}
              style={{ display: "flex", justifyContent: "space-between" }}
            >
              <span>
                {b.name} {b.is_active ? "" : "(inactiva)"}
              </span>
              <button onClick={() => handleDelete(b.id)}>Eliminar</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
