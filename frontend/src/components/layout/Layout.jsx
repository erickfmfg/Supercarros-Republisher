import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h2>SuperCarros</h2>
        <nav>
          <NavLink to="/" end>
            Inicio
          </NavLink>
          <NavLink to="/schedules">Programar republicación</NavLink>
          <NavLink to="/manual">Republicación manual</NavLink>
          <NavLink to="/brands">Marcas</NavLink>
          <NavLink to="/settings">Configuración</NavLink>
        </nav>
        <div style={{ marginTop: "auto", fontSize: "0.875rem" }}>
          {user && (
            <>
              <div>{user.username}</div>
              <button
                style={{ marginTop: "0.5rem", width: "100%" }}
                onClick={logout}
              >
                Cerrar sesión
              </button>
            </>
          )}
        </div>
      </aside>
      <main className="main-content">
        <div className="topbar">
          <h1>Panel de republicación</h1>
        </div>
        {children}
      </main>
    </div>
  );
}
