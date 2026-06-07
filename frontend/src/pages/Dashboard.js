import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import {
  TrendingUp, AlertTriangle, CheckCircle2, Clock, FileText,
  Zap, ArrowRight, ShieldCheck, Activity
} from "lucide-react";
import { api } from "../services/api";

const statusColor = { draft: "#888", assigned: "#a580ff", in_progress: "#4d9fff", validated: "#00e5a0", complete: "#00e5a0" };
const severityColor = { critical: "#ff3d5a", high: "#ff8c00", medium: "#f5c842", low: "#00d4ff" };

function StatCard({ icon, label, value, delta, deltaUp, accentColor, accentBg }) {
  return (
    <div className="stat-card" style={{ "--accent-color": accentColor, "--accent-bg": accentBg }}>
      {delta && <span className={`stat-delta ${deltaUp ? "delta-up" : "delta-down"}`}>{delta}</span>}
      <div className="stat-icon" style={{ background: accentBg }}>{icon}</div>
      <div className="stat-value" style={{ color: accentColor }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "rgba(8,18,32,0.95)", border: "1px solid rgba(0,180,255,0.2)", borderRadius: 8, padding: "10px 14px" }}>
      <p style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)", marginBottom: 4 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15, color: p.color }}>{p.value}{p.name === "rate" ? "%" : ""}</p>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [trend, setTrend] = useState([]);
  const [circulars, setCirculars] = useState([]);
  const [depts, setDepts] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    api.getDashboardStats().then(d => d && setStats(d));
    api.getComplianceTrend().then(d => d && setTrend(d.trend));
    api.getCirculars().then(d => d && setCirculars(d.circulars.slice(0, 5)));
    api.getDepartments().then(d => d && setDepts(d.departments));
    api.getAgentLogs().then(d => d && setLogs(d.logs.slice(0, 5)));
  }, []);

  if (!stats) return <div className="page"><div className="loading-pulse" style={{ color: "var(--text-dim)", padding: 40 }}>Loading dashboard...</div></div>;

  const pieData = [
    { name: "Complete", value: stats.complete_tasks, color: "#00e5a0" },
    { name: "In Progress", value: stats.in_progress_tasks, color: "#4d9fff" },
    { name: "Other", value: stats.total_tasks - stats.complete_tasks - stats.in_progress_tasks, color: "rgba(255,255,255,0.08)" },
  ];

  return (
    <div className="page fade-in">
      {/* KPI row */}
      <div className="stats-grid">
        <StatCard icon={<FileText size={16} color="#00d4ff" />} label="Total Circulars" value={stats.total_circulars}
          delta="+2 this month" deltaUp accentColor="var(--accent-cyan)" accentBg="rgba(0,212,255,0.1)" />
        <StatCard icon={<ShieldCheck size={16} color="#00e5a0" />} label="Compliance Rate" value={`${stats.compliance_rate}%`}
          delta="+4.2%" deltaUp accentColor="var(--accent-green)" accentBg="rgba(0,229,160,0.1)" />
        <StatCard icon={<Clock size={16} color="#f5c842" />} label="Tasks In Progress" value={stats.in_progress_tasks}
          delta={`${stats.overdue_tasks} overdue`} accentColor="var(--accent-gold)" accentBg="rgba(245,200,66,0.1)" />
        <StatCard icon={<AlertTriangle size={16} color="#ff3d5a" />} label="Critical Alerts" value={stats.critical_alerts}
          accentColor="var(--accent-red)" accentBg="rgba(255,61,90,0.1)" />
      </div>

      {/* Row 2: Trend + Pie + Logs */}
      <div className="grid-3-1" style={{ marginBottom: 20 }}>
        <div>
          <div className="grid-2" style={{ marginBottom: 20 }}>
            {/* Compliance Trend */}
            <div className="card">
              <div className="card-header">
                <div className="card-title"><TrendingUp size={14} color="var(--accent-cyan)" /> Compliance Trend</div>
                <span className="chip"><Activity size={10} /> 6mo</span>
              </div>
              <div className="card-body" style={{ padding: "12px 16px 16px" }}>
                <ResponsiveContainer width="100%" height={140}>
                  <AreaChart data={trend}>
                    <defs>
                      <linearGradient id="cGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fill: "var(--text-dim)", fontSize: 10, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "var(--text-dim)", fontSize: 10, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} domain={[40, 100]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="rate" stroke="#00d4ff" strokeWidth={2} fill="url(#cGrad)" dot={{ fill: "#00d4ff", r: 3 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Task Status Donut */}
            <div className="card">
              <div className="card-header">
                <div className="card-title"><CheckCircle2 size={14} color="var(--accent-green)" /> Task Status</div>
              </div>
              <div className="card-body" style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 16 }}>
                <ResponsiveContainer width={110} height={110}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={32} outerRadius={52} dataKey="value" paddingAngle={3}>
                      {pieData.map((entry, i) => <Cell key={i} fill={entry.color} stroke="none" />)}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ flex: 1 }}>
                  {pieData.map((d, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: d.color, flexShrink: 0 }} />
                      <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>{d.name}</span>
                      <span style={{ marginLeft: "auto", fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 13, color: d.color }}>{d.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Circulars */}
          <div className="card">
            <div className="card-header">
              <div className="card-title"><FileText size={14} color="var(--accent-cyan)" /> Recent Circulars</div>
              <Link to="/circulars" style={{ textDecoration: "none" }}>
                <button className="btn btn-ghost btn-sm">View All <ArrowRight size={11} /></button>
              </Link>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Circular</th><th>Severity</th><th>Status</th><th>Progress</th></tr>
                </thead>
                <tbody>
                  {circulars.map(c => {
                    const pct = c.task_count > 0 ? Math.round((c.completed_tasks / c.task_count) * 100) : 0;
                    return (
                      <tr key={c.id}>
                        <td>
                          <Link to={`/circulars/${encodeURIComponent(c.id)}`} style={{ textDecoration: "none" }}>
                            <span className="circular-id">{c.id}</span>
                            <span className="circular-title-cell">{c.title.substring(0, 45)}{c.title.length > 45 ? "…" : ""}</span>
                          </Link>
                        </td>
                        <td><span className={`badge badge-${c.severity}`}>{c.severity}</span></td>
                        <td><span className={`badge badge-${c.status === "in_progress" ? "progress" : c.status}`}>{c.status.replace("_", " ")}</span></td>
                        <td>
                          <div style={{ minWidth: 80 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                              <span>{c.completed_tasks}/{c.task_count}</span><span>{pct}%</span>
                            </div>
                            <div className="progress-bar">
                              <div className="progress-fill" style={{ width: `${pct}%`, background: pct === 100 ? "var(--accent-green)" : "var(--accent-cyan)" }} />
                            </div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right column: Dept + Logs */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Dept snapshot */}
          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <div className="card-title"><Zap size={14} color="var(--accent-gold)" /> Dept. Compliance</div>
            </div>
            <div className="card-body" style={{ padding: "12px 16px" }}>
              {depts.map(d => (
                <div key={d.id} style={{ marginBottom: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 12, fontWeight: 600 }}>{d.name}</span>
                    <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 13, color: d.completion_rate >= 80 ? "var(--accent-green)" : d.completion_rate >= 50 ? "var(--accent-gold)" : "var(--accent-red)" }}>
                      {d.completion_rate}%
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{
                      width: `${d.completion_rate}%`,
                      background: d.completion_rate >= 80 ? "var(--accent-green)" : d.completion_rate >= 50 ? "var(--accent-gold)" : "var(--accent-red)"
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Agent log */}
          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <div className="card-title"><Activity size={14} color="var(--accent-purple)" /> Agent Activity</div>
              <Link to="/agents" style={{ textDecoration: "none" }}>
                <button className="btn btn-ghost btn-sm">Logs <ArrowRight size={11} /></button>
              </Link>
            </div>
            <div className="card-body" style={{ padding: "8px 16px" }}>
              {logs.map(l => (
                <div key={l.id} className="log-entry">
                  <div className="log-dot" style={{ background: l.status === "success" ? "var(--accent-green)" : l.status === "pending" ? "var(--accent-gold)" : "var(--accent-red)" }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", gap: 8, marginBottom: 2 }}>
                      <span className="log-agent">{l.agent}</span>
                      <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>{l.action}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.4 }}>{l.message.substring(0, 70)}…</div>
                    <div className="log-time">{new Date(l.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
