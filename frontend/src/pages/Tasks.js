import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ClipboardList, Search, AlertCircle, Clock } from "lucide-react";
import { api } from "../services/api";

const COLS = [
  { key: "draft", label: "Draft", color: "rgba(255,255,255,0.4)" },
  { key: "assigned", label: "Assigned", color: "#a580ff" },
  { key: "in_progress", label: "In Progress", color: "#4d9fff" },
  { key: "validated", label: "Validated", color: "#00e5a0" },
  { key: "complete", label: "Complete", color: "#00e5a0" },
];

const PRIORITY_COLOR = { critical: "#ff3d5a", high: "#ff8c00", medium: "#f5c842", low: "#00d4ff" };

function TaskCard({ task }) {
  return (
    <div style={{
      background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 10, padding: "12px 14px",
      marginBottom: 8, cursor: "default", transition: "all 0.2s"
    }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--border-bright)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.transform = "none"; }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)" }}>{task.id}</span>
        <span className={`badge badge-${task.priority}`} style={{ padding: "1px 6px", fontSize: 9 }}>{task.priority}</span>
      </div>
      <p style={{ fontSize: 12, fontWeight: 500, lineHeight: 1.5, marginBottom: 8, color: "var(--text-primary)" }}>{task.description}</p>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: 10, background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)", padding: "2px 7px", borderRadius: 5, color: "var(--text-secondary)" }}>{task.assigned_department}</span>
        <span style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "var(--font-mono)", display: "flex", alignItems: "center", gap: 3, marginLeft: "auto" }}>
          <Clock size={9} /> {task.due_date}
        </span>
      </div>
      <div style={{ marginTop: 8 }}>
        <Link to={`/circulars/${encodeURIComponent(task.circular_id)}`} style={{ textDecoration: "none" }}>
          <span style={{ fontSize: 10, color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>{task.circular_id}</span>
        </Link>
      </div>
    </div>
  );
}

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [search, setSearch] = useState("");
  const [view, setView] = useState("kanban");

  useEffect(() => {
    api.getTasks().then(d => d && setTasks(d.tasks));
  }, []);

  const filtered = tasks.filter(t =>
    !search || t.description.toLowerCase().includes(search.toLowerCase()) ||
    t.assigned_department.toLowerCase().includes(search.toLowerCase()) ||
    t.circular_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page fade-in">
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ position: "relative", flex: "1 1 240px", maxWidth: 340 }}>
          <Search size={13} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-dim)" }} />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search tasks…"
            style={{ width: "100%", padding: "8px 12px 8px 32px", background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)", fontSize: 13, outline: "none", fontFamily: "var(--font-body)" }} />
        </div>
        <div style={{ display: "flex", gap: 4, marginLeft: "auto" }}>
          {["kanban", "list"].map(v => (
            <button key={v} className={`btn btn-${view === v ? "primary" : "ghost"} btn-sm`} onClick={() => setView(v)}
              style={{ textTransform: "capitalize" }}>{v}</button>
          ))}
        </div>
      </div>

      {view === "kanban" ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 14, alignItems: "start" }}>
          {COLS.map(col => {
            const colTasks = filtered.filter(t => t.status === col.key);
            return (
              <div key={col.key}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, padding: "0 2px" }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: col.color }} />
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: 1 }}>{col.label}</span>
                  <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-dim)", background: "rgba(255,255,255,0.05)", padding: "1px 6px", borderRadius: 10 }}>{colTasks.length}</span>
                </div>
                <div style={{ minHeight: 60 }}>
                  {colTasks.map(t => <TaskCard key={t.id} task={t} />)}
                  {colTasks.length === 0 && <div style={{ padding: "20px 8px", textAlign: "center", color: "var(--text-dim)", fontSize: 11, border: "1px dashed rgba(255,255,255,0.07)", borderRadius: 8 }}>Empty</div>}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Task ID</th><th>Description</th><th>Circular</th><th>Department</th><th>Priority</th><th>Status</th><th>Due Date</th></tr></thead>
              <tbody>
                {filtered.map(t => (
                  <tr key={t.id}>
                    <td><span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-dim)" }}>{t.id}</span></td>
                    <td style={{ maxWidth: 280 }}>{t.description}</td>
                    <td><Link to={`/circulars/${encodeURIComponent(t.circular_id)}`} style={{ color: "var(--accent-cyan)", textDecoration: "none", fontFamily: "var(--font-mono)", fontSize: 11 }}>{t.circular_id}</Link></td>
                    <td><span style={{ fontSize: 12 }}>{t.assigned_department}</span></td>
                    <td><span className={`badge badge-${t.priority}`}>{t.priority}</span></td>
                    <td><span className={`badge badge-${t.status === "in_progress" ? "progress" : t.status}`}>{t.status.replace("_", " ")}</span></td>
                    <td><span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)" }}>{t.due_date}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
