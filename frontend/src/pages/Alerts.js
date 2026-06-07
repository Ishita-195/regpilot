import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Bell, AlertTriangle, AlertCircle, CheckCircle2, Info, Bot, ArrowRight } from "lucide-react";
import { api } from "../services/api";

const ALERT_TYPE_ICON = {
  deadline: <Clock />, new_circular: <Bell />, overdue: <AlertTriangle />,
  validation: <CheckCircle2 />, agent: <Bot />
};

function Clock() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>; }

const SEV_ICON = { critical: <AlertTriangle size={14} />, high: <AlertCircle size={14} />, medium: <Info size={14} />, low: <Bell size={14} /> };
const SEV_COLOR = { critical: "#ff3d5a", high: "#ff8c00", medium: "#f5c842", low: "#00d4ff" };
const SEV_BG = { critical: "rgba(255,61,90,0.1)", high: "rgba(255,140,0,0.1)", medium: "rgba(245,200,66,0.1)", low: "rgba(0,212,255,0.08)" };

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    api.getAlerts().then(d => d && setAlerts(d.alerts));
  }, []);

  const markRead = async (id) => {
    await api.markAlertRead(id);
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
  };

  const displayed = filter === "all" ? alerts : filter === "unread" ? alerts.filter(a => !a.read) : alerts.filter(a => a.severity === filter);
  const unreadCount = alerts.filter(a => !a.read).length;

  return (
    <div className="page fade-in">
      {/* Summary */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {["all", "unread", "critical", "high", "medium", "low"].map(f => (
            <button key={f} className={`btn btn-${filter === f ? "primary" : "ghost"} btn-sm`} onClick={() => setFilter(f)} style={{ textTransform: "capitalize" }}>
              {f === "all" ? `All (${alerts.length})` : f === "unread" ? `Unread (${unreadCount})` : f}
            </button>
          ))}
        </div>
        {unreadCount > 0 && (
          <button className="btn btn-ghost btn-sm" style={{ marginLeft: "auto" }} onClick={() => alerts.filter(a => !a.read).forEach(a => markRead(a.id))}>
            Mark all read
          </button>
        )}
      </div>

      {/* Alert list */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {displayed.map(alert => (
          <div key={alert.id} className="card" style={{
            opacity: alert.read ? 0.65 : 1,
            transition: "all 0.3s",
            borderColor: alert.read ? "var(--border)" : `${SEV_COLOR[alert.severity]}30`,
          }}>
            <div style={{ padding: "16px 20px", display: "flex", gap: 14, alignItems: "flex-start" }}>
              <div style={{
                width: 38, height: 38, borderRadius: 10, flexShrink: 0,
                background: SEV_BG[alert.severity],
                border: `1px solid ${SEV_COLOR[alert.severity]}25`,
                display: "flex", alignItems: "center", justifyContent: "center",
                color: SEV_COLOR[alert.severity]
              }}>
                {SEV_ICON[alert.severity]}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 4 }}>
                  <span style={{ fontWeight: 700, fontSize: 14, fontFamily: "var(--font-display)" }}>{alert.title}</span>
                  <span className={`badge badge-${alert.severity}`}>{alert.severity}</span>
                  {!alert.read && <span style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--accent-cyan)", boxShadow: "var(--glow-cyan)", display: "inline-block" }} />}
                </div>
                <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 6 }}>{alert.message}</p>
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)" }}>{new Date(alert.timestamp).toLocaleString()}</span>
                  {alert.circular_id && (
                    <Link to={`/circulars/${encodeURIComponent(alert.circular_id)}`} style={{ textDecoration: "none" }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--accent-cyan)", display: "flex", alignItems: "center", gap: 3 }}>
                        {alert.circular_id} <ArrowRight size={9} />
                      </span>
                    </Link>
                  )}
                </div>
              </div>
              {!alert.read && (
                <button className="btn btn-ghost btn-sm" onClick={() => markRead(alert.id)} style={{ flexShrink: 0, fontSize: 11 }}>
                  <CheckCircle2 size={11} /> Mark read
                </button>
              )}
            </div>
          </div>
        ))}
        {displayed.length === 0 && (
          <div className="empty-state">
            <Bell size={32} style={{ margin: "0 auto 12px", color: "var(--text-dim)" }} />
            <p>No alerts in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
}
