import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Bot, Calendar, ClipboardList, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "../services/api";

const STATUS_STEPS = ["draft", "assigned", "in_progress", "validated", "complete"];

function TaskRow({ task, onValidate }) {
  const [validating, setValidating] = useState(false);
  const handleValidate = async () => {
    setValidating(true);
    await onValidate(task.id);
    setValidating(false);
  };

  return (
    <tr>
      <td>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)", marginBottom: 2 }}>{task.id}</div>
        <div style={{ fontWeight: 500 }}>{task.description}</div>
      </td>
      <td>
        <span style={{ fontSize: 12, color: "var(--text-secondary)", background: "rgba(255,255,255,0.04)", padding: "3px 8px", borderRadius: 6, border: "1px solid var(--border)" }}>{task.assigned_department}</span>
      </td>
      <td><span className={`badge badge-${task.priority}`}>{task.priority}</span></td>
      <td><span className={`badge badge-${task.status === "in_progress" ? "progress" : task.status}`}>{task.status.replace("_", " ")}</span></td>
      <td>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)" }}>{task.due_date}</span>
      </td>
      <td>
        {task.status !== "complete" && task.status !== "validated" && (
          <button className="btn btn-ghost btn-sm" onClick={handleValidate} disabled={validating} style={{ fontSize: 11 }}>
            {validating ? "…" : <><CheckCircle2 size={11} /> Validate</>}
          </button>
        )}
        {(task.status === "complete" || task.status === "validated") && (
          <span style={{ color: "var(--accent-green)", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
            <CheckCircle2 size={12} /> Done
          </span>
        )}
      </td>
    </tr>
  );
}

export default function CircularDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getCircular(decodeURIComponent(id)).then(d => d && setData(d));
  }, [id]);

  const handleValidate = async (taskId) => {
    await api.validateTask(taskId);
    const fresh = await api.getCircular(decodeURIComponent(id));
    if (fresh) setData(fresh);
  };

  if (!data) return <div className="page"><div className="loading-pulse" style={{ color: "var(--text-dim)", padding: 40 }}>Loading circular…</div></div>;

  const pct = data.tasks.length > 0 ? Math.round((data.tasks.filter(t => t.status === "complete" || t.status === "validated").length / data.tasks.length) * 100) : 0;

  return (
    <div className="page fade-in">
      {/* Back */}
      <Link to="/circulars" style={{ textDecoration: "none" }}>
        <button className="btn btn-ghost btn-sm" style={{ marginBottom: 16 }}>
          <ArrowLeft size={13} /> Back to Circulars
        </button>
      </Link>

      {/* Header card */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ padding: "20px 24px" }}>
          <div style={{ display: "flex", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 280 }}>
              <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--accent-cyan)" }}>{data.id}</span>
                <span className={`badge badge-${data.severity}`}>{data.severity}</span>
                <span className={`badge badge-${data.status === "in_progress" ? "progress" : data.status}`}>{data.status.replace("_", " ")}</span>
                <span className="chip">{data.category}</span>
              </div>
              <h2 style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{data.title}</h2>
              <div style={{ display: "flex", gap: 16, fontSize: 12, color: "var(--text-secondary)" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Calendar size={11} /> Issued: {data.date_issued}</span>
                <span style={{ display: "flex", alignItems: "center", gap: 4 }}><ClipboardList size={11} /> {data.tasks.length} Tasks</span>
              </div>
            </div>
            <div style={{ textAlign: "right", minWidth: 120 }}>
              <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 36, color: pct === 100 ? "var(--accent-green)" : "var(--accent-cyan)", lineHeight: 1 }}>{pct}%</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)", marginTop: 4 }}>COMPLETE</div>
              <div className="progress-bar" style={{ marginTop: 8, height: 6 }}>
                <div className="progress-fill" style={{ width: `${pct}%`, height: 6, background: pct === 100 ? "var(--accent-green)" : "linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))", boxShadow: "0 0 8px var(--accent-cyan)" }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Summary */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title"><Bot size={14} color="var(--accent-purple)" /> AI Compliance Summary</div>
          <span className="chip" style={{ color: "var(--accent-purple)", borderColor: "rgba(124,77,255,0.25)" }}><Bot size={9} /> Claude-powered</span>
        </div>
        <div style={{ padding: "14px 20px", background: "rgba(124,77,255,0.04)", borderRadius: "0 0 16px 16px" }}>
          <p style={{ fontSize: 13, color: "var(--text-primary)", lineHeight: 1.7 }}>{data.ai_summary}</p>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 10, lineHeight: 1.6 }}><strong style={{ color: "var(--text-primary)" }}>Original text:</strong> {data.content}</p>
        </div>
      </div>

      {/* Task pipeline status */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title"><AlertCircle size={14} color="var(--accent-gold)" /> Pipeline Progress</div>
        </div>
        <div style={{ padding: "16px 24px", display: "flex", gap: 0, alignItems: "center" }}>
          {STATUS_STEPS.map((step, i) => {
            const taskCount = data.tasks.filter(t => t.status === step).length;
            const isActive = data.tasks.some(t => t.status === step);
            const isDone = STATUS_STEPS.indexOf(step) < STATUS_STEPS.indexOf(data.status);
            return (
              <React.Fragment key={step}>
                <div style={{ textAlign: "center", flex: 1 }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: "50%", margin: "0 auto 6px",
                    background: isDone ? "var(--accent-green)" : isActive ? "var(--accent-cyan)" : "rgba(255,255,255,0.05)",
                    border: `2px solid ${isDone ? "var(--accent-green)" : isActive ? "var(--accent-cyan)" : "rgba(255,255,255,0.1)"}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)",
                    color: isDone || isActive ? "#000" : "var(--text-dim)",
                    boxShadow: isActive ? "var(--glow-cyan)" : isDone ? "var(--glow-green)" : "none",
                    transition: "all 0.3s"
                  }}>{taskCount || (isDone ? "✓" : "")}</div>
                  <div style={{ fontSize: 10, fontFamily: "var(--font-mono)", color: isActive ? "var(--accent-cyan)" : isDone ? "var(--accent-green)" : "var(--text-dim)", textTransform: "uppercase", letterSpacing: 1 }}>{step.replace("_", " ")}</div>
                </div>
                {i < STATUS_STEPS.length - 1 && (
                  <div style={{ flex: 0.5, height: 2, background: i < STATUS_STEPS.indexOf(data.status) ? "var(--accent-green)" : "rgba(255,255,255,0.08)", marginBottom: 20 }} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Tasks table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><ClipboardList size={14} color="var(--accent-cyan)" /> Tasks ({data.tasks.length})</div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Task</th><th>Department</th><th>Priority</th><th>Status</th><th>Due Date</th><th>Action</th></tr>
            </thead>
            <tbody>
              {data.tasks.map(t => <TaskRow key={t.id} task={t} onValidate={handleValidate} />)}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
