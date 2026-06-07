import React, { useState, useEffect } from "react";
import { Building2, Mail, User, CheckCircle2, Clock } from "lucide-react";
import { api } from "../services/api";

function DeptCard({ dept }) {
  const rate = dept.completion_rate;
  const color = rate >= 80 ? "var(--accent-green)" : rate >= 50 ? "var(--accent-gold)" : "var(--accent-red)";
  const glow = rate >= 80 ? "var(--glow-green)" : rate >= 50 ? "var(--glow-gold)" : "var(--glow-red)";

  return (
    <div className="dept-card">
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 12 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10, background: `rgba(${rate >= 80 ? "0,229,160" : rate >= 50 ? "245,200,66" : "255,61,90"},0.1)`,
          display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
          border: `1px solid ${color}30`
        }}>
          <Building2 size={16} color={color} />
        </div>
        <div style={{ flex: 1 }}>
          <div className="dept-name">{dept.name}</div>
          <div className="dept-head" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <User size={10} /> {dept.head}
          </div>
        </div>
        <div className="dept-rate" style={{ color }}>{rate}%</div>
      </div>

      <div className="progress-bar" style={{ height: 5, marginBottom: 12 }}>
        <div className="progress-fill" style={{ width: `${rate}%`, height: 5, background: color, boxShadow: glow }} />
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <div style={{ flex: 1, textAlign: "center", padding: "8px", background: "rgba(0,229,160,0.06)", borderRadius: 8, border: "1px solid rgba(0,229,160,0.12)" }}>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16, color: "var(--accent-green)" }}>{dept.completed}</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: 1 }}>Done</div>
        </div>
        <div style={{ flex: 1, textAlign: "center", padding: "8px", background: "rgba(255,140,0,0.06)", borderRadius: 8, border: "1px solid rgba(255,140,0,0.12)" }}>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16, color: "var(--accent-orange)" }}>{dept.pending}</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: 1 }}>Pending</div>
        </div>
        <div style={{ flex: 1, textAlign: "center", padding: "8px", background: "rgba(0,212,255,0.06)", borderRadius: 8, border: "1px solid rgba(0,212,255,0.12)" }}>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16, color: "var(--accent-cyan)" }}>{dept.total_tasks}</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: 1 }}>Total</div>
        </div>
      </div>

      <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--text-secondary)" }}>
        <Mail size={11} />
        <span>{dept.email}</span>
      </div>
    </div>
  );
}

export default function Departments() {
  const [depts, setDepts] = useState([]);

  useEffect(() => {
    api.getDepartments().then(d => d && setDepts(d.departments));
  }, []);

  const overall = depts.length ? Math.round(depts.reduce((s, d) => s + d.completion_rate, 0) / depts.length) : 0;

  return (
    <div className="page fade-in">
      {/* Summary bar */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ padding: "20px 24px", display: "flex", gap: 32, flexWrap: "wrap", alignItems: "center" }}>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontSize: 36, fontWeight: 800, color: "var(--accent-green)", lineHeight: 1 }}>{overall}%</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)", marginTop: 4 }}>OVERALL COMPLIANCE</div>
          </div>
          <div className="divider" style={{ width: 1, height: 50, margin: 0 }} />
          {[
            { label: "Departments", val: depts.length, icon: <Building2 size={14} />, color: "var(--accent-cyan)" },
            { label: "Total Tasks", val: depts.reduce((s, d) => s + d.total_tasks, 0), icon: <Clock size={14} />, color: "var(--accent-gold)" },
            { label: "Completed", val: depts.reduce((s, d) => s + d.completed, 0), icon: <CheckCircle2 size={14} />, color: "var(--accent-green)" },
          ].map(({ label, val, icon, color }) => (
            <div key={label}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, color, marginBottom: 2 }}>{icon}<span style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700 }}>{val}</span></div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)" }}>{label.toUpperCase()}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid-dept">
        {depts.map(d => <DeptCard key={d.id} dept={d} />)}
      </div>
    </div>
  );
}
