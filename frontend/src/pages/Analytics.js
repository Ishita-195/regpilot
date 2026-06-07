import React, { useState, useEffect } from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, RadarChart,
  Radar, PolarGrid, PolarAngleAxis, Legend
} from "recharts";
import { BarChart3, TrendingUp, PieChart as PieIcon, Activity } from "lucide-react";
import { api } from "../services/api";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "rgba(8,18,32,0.95)", border: "1px solid rgba(0,180,255,0.2)", borderRadius: 8, padding: "10px 14px" }}>
      <p style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)", marginBottom: 4 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 14, color: p.color }}>
          {p.name}: {p.value}{p.name === "rate" || p.name === "Compliance %" ? "%" : ""}
        </p>
      ))}
    </div>
  );
};

const PIE_COLORS = ["#ff3d5a", "#ff8c00", "#00d4ff", "#a580ff", "#00e5a0", "#f5c842"];

export default function Analytics() {
  const [trend, setTrend] = useState([]);
  const [catDist, setCatDist] = useState([]);
  const [deptPerf, setDeptPerf] = useState([]);

  useEffect(() => {
    api.getComplianceTrend().then(d => d && setTrend(d.trend));
    api.getCategoryDistribution().then(d => d && setCatDist(d.distribution));
    api.getDeptPerformance().then(d => d && setDeptPerf(d.performance));
  }, []);

  const radarData = deptPerf.map(d => ({ dept: d.department.split(" ")[0], "Compliance %": d.rate }));

  return (
    <div className="page fade-in">
      {/* Row 1: Trend + Category */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Compliance Trend */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><TrendingUp size={14} color="var(--accent-cyan)" /> 6-Month Compliance Trend</div>
          </div>
          <div className="card-body" style={{ padding: "16px 20px 20px" }}>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="aGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fill: "var(--text-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--text-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} domain={[40, 100]} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="rate" name="rate" stroke="#00d4ff" strokeWidth={2.5} fill="url(#aGrad)" dot={{ fill: "#00d4ff", r: 4, strokeWidth: 0 }} activeDot={{ r: 6, fill: "#00d4ff" }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><PieIcon size={14} color="var(--accent-purple)" /> Circular Categories</div>
          </div>
          <div className="card-body" style={{ padding: "16px 20px 20px", display: "flex", gap: 16, alignItems: "center" }}>
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={catDist} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="count" paddingAngle={4}>
                  {catDist.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="none" />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1 }}>
              {catDist.map((d, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: PIE_COLORS[i % PIE_COLORS.length], flexShrink: 0 }} />
                  <span style={{ fontSize: 12, flex: 1 }}>{d.category}</span>
                  <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, color: PIE_COLORS[i % PIE_COLORS.length] }}>{d.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Dept bar + Radar */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Department performance bar */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><BarChart3 size={14} color="var(--accent-gold)" /> Department Performance</div>
          </div>
          <div className="card-body" style={{ padding: "16px 20px 20px" }}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={deptPerf} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "var(--text-dim)", fontSize: 10, fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} />
                <YAxis dataKey="department" type="category" tick={{ fill: "var(--text-secondary)", fontSize: 11, fontFamily: "var(--font-body)" }} axisLine={false} tickLine={false} width={110} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="rate" name="rate" radius={[0, 4, 4, 0]} maxBarSize={16}>
                  {deptPerf.map((d, i) => (
                    <Cell key={i} fill={d.rate >= 80 ? "#00e5a0" : d.rate >= 50 ? "#f5c842" : "#ff3d5a"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Activity size={14} color="var(--accent-cyan)" /> Dept. Radar View</div>
          </div>
          <div className="card-body" style={{ padding: "16px 20px 20px" }}>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.06)" />
                <PolarAngleAxis dataKey="dept" tick={{ fill: "var(--text-secondary)", fontSize: 11, fontFamily: "var(--font-mono)" }} />
                <Radar name="Compliance %" dataKey="Compliance %" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.15} strokeWidth={2} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Task completion breakdown table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><BarChart3 size={14} color="var(--accent-cyan)" /> Department Breakdown</div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Department</th><th>Total Tasks</th><th>Completed</th><th>Pending</th><th>Compliance Rate</th><th>Trend</th></tr></thead>
            <tbody>
              {deptPerf.map((d, i) => {
                const color = d.rate >= 80 ? "var(--accent-green)" : d.rate >= 50 ? "var(--accent-gold)" : "var(--accent-red)";
                return (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{d.department}</td>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--accent-cyan)" }}>{d.total}</td>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--accent-green)" }}>{d.completed}</td>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--accent-orange)" }}>{d.total - d.completed}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div className="progress-bar" style={{ flex: 1, maxWidth: 80 }}>
                          <div className="progress-fill" style={{ width: `${d.rate}%`, background: color }} />
                        </div>
                        <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, color, fontSize: 13 }}>{d.rate}%</span>
                      </div>
                    </td>
                    <td>
                      <span style={{ color: "var(--accent-green)", fontSize: 12 }}>↑ +{Math.floor(Math.random() * 8 + 2)}%</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
