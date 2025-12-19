import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import SchedulesPage from "./pages/SchedulesPage";
import BrandsPage from "./pages/BrandsPage";
import SettingsPage from "./pages/SettingsPage";
import ManualRepublishPage from "./pages/ManualRepublishPage";
import Layout from "./components/layout/Layout";

const PrivateRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/schedules" element={<SchedulesPage />} />
                <Route path="/manual" element={<ManualRepublishPage />} />
                <Route path="/brands" element={<BrandsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
