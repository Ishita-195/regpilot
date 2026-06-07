import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FileText, Search, Filter, ChevronRight, Calendar, Layers } from "lucide-react";
import { api } from "../services/api";

const STATUS_OPTS = ["all", "draft", "assigned", "in_progress", "complete"];
const SEV_OPTS = ["all", "critical", "high", "medium", "low"];

export default function Circulars() {
  const [circulars, setCirculars] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [severity, setSeverity] = useState("all");

  useEffect(() => {
    api.getCirculars().then(d => {
      if (d) { setCirculars(d.circulars); setFiltered(d.circulars); }
    });
  }, []);

  useEffect(() => {
    let result = circulars;
    if (status !== "all") result = result.filter(c => c.status === status);
    if (severity !== "all") result = result.filter(c => c.severity === severity);
    if (search) result = result.filter(c =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.id.toLowerCase().includes(search.toLowerCase()) ||
      c.category.toLowerCase().includes(search.toLowerCase())
    );
    setFiltered(result);
  }, [search, status, severity, circulars]);

  return (
    <div className="page fade-in">
      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ position: "relative", flex: "1 1 240px", maxWidth: 340 }}>
          <Search size={13} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-dim)" }} />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search circulars…"
            style={{ width: "100%", padding: "8px 12px 8px 32px", background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-primary)", fontSize: 13, outline: "none", fontFamily: "var(--font-body)" }} />
        </div>
        <select value={status} onChange={e => setStatus(e.target.value)}
          style={{ padding: "8px 12px", background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-secondary)", fontSize: 12, outline: "none", fontFamily: "var(--font-mono)", cursor: "pointer" }}>
          {STATUS_OPTS.map(s => <option key={s} value={s}>{s === "all" ? "All Statuses" : s.replace("_", " ")}</option>)}
        </select>
        <select value={severity} onChange={e => setSeverity(e.target.value)}
          style={{ padding: "8px 12px", background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-secondary)", fontSize: 12, outline: "none", fontFamily: "var(--font-mono)", cursor: "pointer" }}>
          {SEV_OPTS.map(s => <option key={s} value={s}>{s === "all" ? "All Severities" : s}</option>)}
        </select>
        <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-dim)" }}>{filtered.length} circulars</span>
      </div>

      {/* Circular cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {filtered.map(c => {
          const pct = c.task_count > 0 ? Math.round((c.completed_tasks / c.task_count) * 100) : 0;
          return (
            <Link key={c.id} to={`/circulars/${encodeURIComponent(c.id)}`} style={{ textDecoration: "none" }}>
              <div className="card" style={{ cursor: "pointer" }}>
                <div style={{ padding: "18px 20px", display: "flex", gap: 16, alignItems: "flex-start" }}>
                  {/* Left icon */}
                  <div style={{
                    width: 44, height: 44, borderRadius: 10, flexShrink: 0,
                    background: c.severity === "critical" ? "rgba(255,61,90,0.12)" : c.severity === "high" ? "rgba(255,140,0,0.12)" : "rgba(0,212,255,0.1)",
                    display: "flex", alignItems: "center", justifyContent: "center"
                  }}>
                    <FileText size={18} color={c.severity === "critical" ? "#ff3d5a" : c.severity === "high" ? "#ff8c00" : "var(--accent-cyan)"} />
                  </div>
                  {/* Main */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 4 }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--accent-cyan)" }}>{c.id}</span>
                      <span className={`badge badge-${c.severity}`}>{c.severity}</span>
                      <span className={`badge badge-${c.status === "in_progress" ? "progress" : c.status}`}>{c.status.replace("_", " ")}</span>
                      <span className="chip" style={{ marginLeft: "auto" }}><Layers size={9} /> {c.category}</span>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: 14, fontFamily: "var(--font-display)", marginBottom: 4 }}>{c.title}</div>
                    <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                      <span style={{ fontSize: 11, color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: 4 }}>
                        <Calendar size={10} /> {c.date_issued}
                      </span>
                      <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>{c.task_count} tasks · {c.completed_tasks} complete</span>
                    </div>
                  </div>
                  {/* Progress */}
                  <div style={{ minWidth: 100, textAlign: "right" }}>
                    <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 20, color: pct === 100 ? "var(--accent-green)" : "var(--accent-cyan)" }}>{pct}%</div>
                    <div className="progress-bar" style={{ marginTop: 4 }}>
                      <div className="progress-fill" style={{ width: `${pct}%`, background: pct === 100 ? "var(--accent-green)" : "linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))" }} />
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "var(--font-mono)", marginTop: 4 }}>complete</div>
                  </div>
                  <ChevronRight size={16} color="var(--text-dim)" style={{ flexShrink: 0, marginTop: 4 }} />
                </div>
              </div>
            </Link>
          );
        })}
        {filtered.length === 0 && <div className="empty-state">No circulars match the current filters.</div>}
      </div>
    </div>
  );
}
