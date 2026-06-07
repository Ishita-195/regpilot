import React, { useState, useEffect } from "react";
import { Bot, Activity, CheckCircle2, Clock, Cpu, Zap, RefreshCw } from "lucide-react";
import { api } from "../services/api";

const AGENT_COLORS = {
  SupervisorAgent: { bg: "rgba(0,212,255,0.12)", color: "#00d4ff", border: "rgba(0,212,255,0.25)" },
  CircularParserAgent: { bg: "rgba(124,77,255,0.12)", color: "#a580ff", border: "rgba(124,77,255,0.25)" },
  TaskRouterAgent: { bg: "rgba(245,200,66,0.12)", color: "#f5c842", border: "rgba(245,200,66,0.25)" },
  ValidatorAgent: { bg: "rgba(0,229,160,0.12)", color: "#00e5a0", border: "rgba(0,229,160,0.25)" },
};

function AgentCard({ agent }) {
  const style = AGENT_COLORS[agent.name] || AGENT_COLORS.SupervisorAgent;
  const isRunning = agent.status === "running";

  return (
    <div className="card" style={{ padding: 20 }}>
      <div style={{ display: "flex", gap: 14, alignItems: "flex-start", marginBottom: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: style.bg, border: `1px solid ${style.border}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Bot size={20} color={style.color} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{agent.name}</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: isRunning ? "var(--accent-green)" : "var(--accent-gold)", boxShadow: isRunning ? "var(--glow-green)" : "var(--glow-gold)", animation: isRunning ? "pulse-dot 2s infinite" : "none" }} />
            <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: isRunning ? "var(--accent-green)" : "var(--accent-gold)" }}>{agent.status.toUpperCase()}</span>
          </div>
        </div>
        <div style={{ background: "rgba(0,229,160,0.08)", border: "1px solid rgba(0,229,160,0.15)", borderRadius: 6, padding: "4px 10px", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--accent-green)" }}>
          {agent.uptime} uptime
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        {Object.entries(agent).filter(([k]) => !["name", "status", "last_run", "uptime"].includes(k)).map(([k, v]) => (
          <div key={k} style={{ background: "rgba(255,255,255,0.03)", borderRadius: 8, padding: "10px 12px", border: "1px solid var(--border)" }}>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15, color: style.color }}>{v}</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: 1, marginTop: 2 }}>{k.replace(/_/g, " ")}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
        <Clock size={10} /> Last run: {new Date(agent.last_run).toLocaleString()}
      </div>
    </div>
  );
}

const LOG_COLOR = { success: "#00e5a0", pending: "#f5c842", error: "#ff3d5a" };

export default function AgentMonitor() {
  const [agents, setAgents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    api.getAgentStatus().then(d => d && setAgents(d.agents));
    api.getAgentLogs().then(d => d && setLogs(d.logs));
  }, []);

  const filteredLogs = filter === "all" ? logs : logs.filter(l => l.status === filter);

  return (
    <div className="page fade-in">
      {/* Workflow diagram */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title"><Cpu size={14} color="var(--accent-cyan)" /> Agent Pipeline Architecture</div>
        </div>
        <div style={{ padding: "20px 24px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto" }}>
            {[
              { label: "RBI Website", sub: "Data Source", icon: "🌐", color: "#00d4ff" },
              { label: "Supervisor Agent", sub: "Orchestrator", icon: "🤖", color: "#00d4ff" },
              { label: "Parser Agent", sub: "Extract MAPs", icon: "📋", color: "#a580ff" },
              { label: "Router Agent", sub: "Dept. Assign", icon: "🗺️", color: "#f5c842" },
              { label: "Validator Agent", sub: "Verify Done", icon: "✅", color: "#00e5a0" },
              { label: "Dashboard", sub: "Live Status", icon: "📊", color: "#4d9fff" },
            ].map((step, i, arr) => (
              <React.Fragment key={step.label}>
                <div style={{ textAlign: "center", minWidth: 100 }}>
                  <div style={{
                    width: 52, height: 52, borderRadius: 12, margin: "0 auto 8px",
                    background: `rgba(${step.color === "#00d4ff" ? "0,212,255" : step.color === "#a580ff" ? "124,77,255" : step.color === "#f5c842" ? "245,200,66" : step.color === "#00e5a0" ? "0,229,160" : "77,159,255"},0.1)`,
                    border: `1px solid ${step.color}30`,
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22
                  }}>{step.icon}</div>
                  <div style={{ fontWeight: 600, fontSize: 11, fontFamily: "var(--font-display)", marginBottom: 2 }}>{step.label}</div>
                  <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>{step.sub}</div>
                </div>
                {i < arr.length - 1 && (
                  <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 2, margin: "0 4px", marginBottom: 20 }}>
                    <div style={{ flex: 1, height: 1, background: "linear-gradient(90deg, rgba(0,212,255,0.3), rgba(0,212,255,0.1))" }} />
                    <div style={{ color: "var(--accent-cyan)", fontSize: 12 }}>▶</div>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Agent status cards */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {agents.map(a => <AgentCard key={a.name} agent={a} />)}
      </div>

      {/* Logs */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><Activity size={14} color="var(--accent-purple)" /> Agent Execution Logs</div>
          <div style={{ display: "flex", gap: 6 }}>
            {["all", "success", "pending", "error"].map(f => (
              <button key={f} className={`btn btn-${filter === f ? "primary" : "ghost"} btn-sm`} onClick={() => setFilter(f)} style={{ textTransform: "capitalize" }}>{f}</button>
            ))}
          </div>
        </div>
        <div style={{ padding: "8px 16px" }}>
          {filteredLogs.map(l => (
            <div key={l.id} className="log-entry">
              <div className="log-dot" style={{ background: LOG_COLOR[l.status] || "#888", boxShadow: `0 0 6px ${LOG_COLOR[l.status] || "#888"}` }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 3 }}>
                  <span className="log-agent">{l.agent}</span>
                  <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-primary)" }}>{l.action}</span>
                  {l.circular_id && (
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--accent-cyan)", background: "rgba(0,212,255,0.08)", padding: "1px 6px", borderRadius: 4 }}>{l.circular_id}</span>
                  )}
                  <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10, color: `${LOG_COLOR[l.status]}`, background: `${LOG_COLOR[l.status]}15`, padding: "1px 7px", borderRadius: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>{l.status}</span>
                </div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 }}>{l.message}</div>
                <div className="log-time">{new Date(l.timestamp).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
