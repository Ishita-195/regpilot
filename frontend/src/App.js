import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard, FileText, ClipboardList, Building2,
  Bot, Bell, BarChart3, Settings, Zap, ChevronRight, RefreshCw
} from "lucide-react";
import "./index.css";
import Dashboard from "./pages/Dashboard";
import Circulars from "./pages/Circulars";
import CircularDetail from "./pages/CircularDetail";
import Tasks from "./pages/Tasks";
import Departments from "./pages/Departments";
import AgentMonitor from "./pages/AgentMonitor";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import { api } from "./services/api";

const PAGE_TITLES = {
  "/": { title: "Compliance Overview", sub: "Real-time regulatory intelligence dashboard" },
  "/circulars": { title: "RBI Circulars", sub: "Ingested and parsed regulatory directives" },
  "/tasks": { title: "Task Management", sub: "Compliance action tracking across departments" },
  "/departments": { title: "Department Status", sub: "Per-department compliance performance" },
  "/agents": { title: "Agent Monitor", sub: "Autonomous workflow orchestration & health" },
  "/alerts": { title: "Alerts & Notifications", sub: "Real-time compliance alerts and warnings" },
  "/analytics": { title: "Analytics", sub: "Compliance trends and performance insights" },
};

function TopBar({ alertCount, onScan, scanning }) {
  const { pathname } = useLocation();
  const info = PAGE_TITLES[pathname] || PAGE_TITLES["/"];
  return (
    <div className="topbar">
      <div className="topbar-left">
        <h1>{info.title}</h1>
        <p>{info.sub}</p>
      </div>
      <div className="topbar-actions">
        <button
          className={`btn btn-ghost btn-sm ${scanning ? "scan-btn-active" : ""}`}
          onClick={onScan}
          disabled={scanning}
          style={{ gap: 6 }}
        >
          <RefreshCw size={13} style={{ animation: scanning ? "spin 1s linear infinite" : "none" }} />
          {scanning ? "Scanning..." : "Trigger Scan"}
        </button>
        <NavLink to="/alerts" style={{ textDecoration: "none" }}>
          <button className="btn btn-ghost btn-sm" style={{ position: "relative" }}>
            <Bell size={14} />
            {alertCount > 0 && (
              <span style={{
                position: "absolute", top: -4, right: -4,
                background: "#ff3d5a", color: "#fff", fontSize: 9,
                fontWeight: 800, borderRadius: "50%", width: 16, height: 16,
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>{alertCount}</span>
            )}
          </button>
        </NavLink>
      </div>
    </div>
  );
}

function Sidebar({ alertCount }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">
          <div className="logo-icon">RP</div>
          <span className="logo-text">RegPilot</span>
        </div>
        <div className="logo-sub">RBI Compliance Agent</div>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section-label">Core</div>
        {[
          { to: "/", icon: <LayoutDashboard size={15} />, label: "Overview" },
          { to: "/circulars", icon: <FileText size={15} />, label: "Circulars" },
          { to: "/tasks", icon: <ClipboardList size={15} />, label: "Tasks" },
          { to: "/departments", icon: <Building2 size={15} />, label: "Departments" },
        ].map(({ to, icon, label }) => (
          <NavLink key={to} to={to} end={to === "/"} style={{ textDecoration: "none" }}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            {icon}<span>{label}</span>
          </NavLink>
        ))}
        <div className="nav-section-label">Intelligence</div>
        {[
          { to: "/agents", icon: <Bot size={15} />, label: "Agent Monitor" },
          { to: "/alerts", icon: <Bell size={15} />, label: "Alerts", badge: alertCount > 0 ? alertCount : null },
          { to: "/analytics", icon: <BarChart3 size={15} />, label: "Analytics" },
        ].map(({ to, icon, label, badge }) => (
          <NavLink key={to} to={to} style={{ textDecoration: "none" }}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            {icon}<span>{label}</span>
            {badge && <span className="nav-badge">{badge}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="agent-status-pill">
          <div className="status-dot" />
          <span>All Agents Active</span>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [alertCount, setAlertCount] = useState(0);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    api.getAlerts().then(d => {
      if (d) setAlertCount(d.alerts.filter(a => !a.read && (a.severity === "critical" || a.severity === "high")).length);
    });
  }, []);

  const handleScan = async () => {
    setScanning(true);
    await api.triggerScan();
    setTimeout(() => setScanning(false), 3000);
  };

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar alertCount={alertCount} />
        <div className="main-content">
          <TopBar alertCount={alertCount} onScan={handleScan} scanning={scanning} />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/circulars" element={<Circulars />} />
            <Route path="/circulars/:id" element={<CircularDetail />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/agents" element={<AgentMonitor />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </div>
      </div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </BrowserRouter>
  );
}
