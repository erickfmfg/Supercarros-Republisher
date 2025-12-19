import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

// ✅ toma el API desde VITE_API_BASE_URL
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
axios.defaults.baseURL = API_BASE_URL;

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      axios
        .get("/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then((res) => setUser(res.data))
        .catch(() => {
          setToken(null);
          setUser(null);
          localStorage.removeItem("token");
        });
    }
  }, [token]);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);

    const res = await axios.post("/api/auth/login", params);
    const t = res.data.access_token;
    setToken(t);
    localStorage.setItem("token", t);

    const me = await axios.get("/api/auth/me", {
      headers: { Authorization: `Bearer ${t}` },
    });
    setUser(me.data);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
