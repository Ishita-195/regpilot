from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from urllib.parse import unquote
from pathlib import Path
import json, random, uuid
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from backend.summarizer import CircularSummarizer
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

# Initialize summarizer
summarizer = CircularSummarizer(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-2-70b-chat")
)
app = FastAPI(title="RegPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-memory mock data ───────────────────────────────────────────────
DEPARTMENTS = [
    {"id": "DEPT-001", "name": "Compliance", "head": "Priya Sharma", "email": "compliance@bank.in"},
    {"id": "DEPT-002", "name": "Risk Management", "head": "Arun Mehta", "email": "risk@bank.in"},
    {"id": "DEPT-003", "name": "Operations", "head": "Sunita Rao", "email": "ops@bank.in"},
    {"id": "DEPT-004", "name": "IT & Cybersecurity", "head": "Vikram Nair", "email": "it@bank.in"},
    {"id": "DEPT-005", "name": "Treasury", "head": "Deepa Iyer", "email": "treasury@bank.in"},
    {"id": "DEPT-006", "name": "Retail Banking", "head": "Rajesh Kumar", "email": "retail@bank.in"},
]

MOCK_CIRCULARS = [
    {
        "id": "RBI/2024/001",
        "title": "Master Direction on KYC - Amendment No. 3",
        "date_issued": "2024-11-10",
        "category": "KYC/AML",
        "severity": "critical",
        "status": "in_progress",
        "content": "This circular amends the Master Direction on Know Your Customer (KYC) to incorporate provisions relating to Central KYC Registry, digital KYC, and video-based customer identification process.",
        "ai_summary": "Critical KYC amendment requiring banks to update digital onboarding workflows, integrate with CKYC registry, and implement V-CIP for remote account opening. Deadline: 90 days.",
        "tasks": [
            {"id": "TASK-001", "description": "Update KYC forms and digital onboarding flows", "assigned_department": "Compliance", "status": "in_progress", "due_date": "2025-02-08", "priority": "high"},
            {"id": "TASK-002", "description": "Integrate with Central KYC Registry (CKYCR)", "assigned_department": "IT & Cybersecurity", "status": "assigned", "due_date": "2025-02-08", "priority": "critical"},
            {"id": "TASK-003", "description": "Train staff on V-CIP procedures", "assigned_department": "Operations", "status": "draft", "due_date": "2025-02-15", "priority": "medium"},
            {"id": "TASK-004", "description": "Update AML/CFT policy documents", "assigned_department": "Risk Management", "status": "validated", "due_date": "2025-01-30", "priority": "high"},
        ]
    },
    {
        "id": "RBI/2024/002",
        "title": "Guidelines on Digital Lending - Revised Framework",
        "date_issued": "2024-11-18",
        "category": "Digital Lending",
        "severity": "high",
        "status": "assigned",
        "content": "Revised guidelines on digital lending to strengthen customer protection, data privacy, and grievance redressal mechanisms for loans sourced digitally.",
        "ai_summary": "New digital lending framework mandates dedicated grievance officer, 30-day loan cooling period, and stricter data sharing controls with LSPs. Significant IT system changes required.",
        "tasks": [
            {"id": "TASK-005", "description": "Appoint dedicated Digital Lending Grievance Officer", "assigned_department": "Compliance", "status": "complete", "due_date": "2025-01-20", "priority": "high"},
            {"id": "TASK-006", "description": "Implement data privacy controls for LSP integrations", "assigned_department": "IT & Cybersecurity", "status": "in_progress", "due_date": "2025-02-20", "priority": "critical"},
            {"id": "TASK-007", "description": "Update loan origination system for cooling-off period", "assigned_department": "IT & Cybersecurity", "status": "assigned", "due_date": "2025-02-28", "priority": "high"},
            {"id": "TASK-008", "description": "Revise LSP agreements and due diligence checklist", "assigned_department": "Operations", "status": "in_progress", "due_date": "2025-02-15", "priority": "medium"},
        ]
    },
    {
        "id": "RBI/2024/003",
        "title": "Cyber Security Framework for Urban Co-operative Banks",
        "date_issued": "2024-12-01",
        "category": "Cybersecurity",
        "severity": "high",
        "status": "draft",
        "content": "Comprehensive cybersecurity framework for UCBs mandating baseline security controls, incident reporting, and third-party risk management.",
        "ai_summary": "Cybersecurity framework requires 24/7 SOC, penetration testing annually, and mandatory incident reporting within 6 hours. Significant investment in security infrastructure needed.",
        "tasks": [
            {"id": "TASK-009", "description": "Establish 24/7 Security Operations Centre (SOC)", "assigned_department": "IT & Cybersecurity", "status": "draft", "due_date": "2025-03-31", "priority": "critical"},
            {"id": "TASK-010", "description": "Conduct annual penetration testing", "assigned_department": "IT & Cybersecurity", "status": "draft", "due_date": "2025-04-30", "priority": "high"},
            {"id": "TASK-011", "description": "Implement incident response plan", "assigned_department": "Risk Management", "status": "assigned", "due_date": "2025-03-15", "priority": "high"},
        ]
    },
    {
        "id": "RBI/2024/004",
        "title": "Prudential Norms on Income Recognition, Asset Classification",
        "date_issued": "2024-12-05",
        "category": "Prudential Norms",
        "severity": "medium",
        "status": "complete",
        "content": "Updated prudential norms on IRAC with revised NPA classification timelines and provisioning requirements.",
        "ai_summary": "IRAC norms update changes NPA recognition to 30 days for certain asset classes. Provisioning requirements increased for sub-standard assets. CBS updates mandatory.",
        "tasks": [
            {"id": "TASK-012", "description": "Update CBS NPA classification logic", "assigned_department": "IT & Cybersecurity", "status": "complete", "due_date": "2025-01-15", "priority": "high"},
            {"id": "TASK-013", "description": "Revise provisioning calculations in reporting system", "assigned_department": "Treasury", "status": "complete", "due_date": "2025-01-15", "priority": "high"},
            {"id": "TASK-014", "description": "Update RBI reporting templates (Schedule 9)", "assigned_department": "Compliance", "status": "complete", "due_date": "2025-01-20", "priority": "medium"},
        ]
    },
    {
        "id": "RBI/2025/001",
        "title": "Framework for Acceptance of Green Deposits",
        "date_issued": "2025-01-03",
        "category": "Green Finance",
        "severity": "medium",
        "status": "in_progress",
        "content": "Framework for regulated entities for acceptance of green deposits, allocation towards green activities, and disclosure requirements.",
        "ai_summary": "Green deposit framework requires third-party verification of fund allocation, quarterly disclosures, and green finance committee at board level. New product category.",
        "tasks": [
            {"id": "TASK-015", "description": "Constitute Board-level Green Finance Committee", "assigned_department": "Compliance", "status": "in_progress", "due_date": "2025-02-28", "priority": "medium"},
            {"id": "TASK-016", "description": "Develop green deposit product and documentation", "assigned_department": "Retail Banking", "status": "draft", "due_date": "2025-03-31", "priority": "medium"},
            {"id": "TASK-017", "description": "Engage third-party verifier for green fund allocation", "assigned_department": "Operations", "status": "draft", "due_date": "2025-03-31", "priority": "low"},
        ]
    },
    {
        "id": "RBI/2025/002",
        "title": "Master Direction – Prepaid Payment Instruments (PPI) – Amendments",
        "date_issued": "2025-01-15",
        "category": "Payments",
        "severity": "critical",
        "status": "in_progress",
        "content": "Amendments to PPI Master Direction expanding wallet interoperability, increasing limits for full-KYC PPIs, and new requirements for PPI issuers.",
        "ai_summary": "PPI amendments double wallet limits to ₹2L, mandate full interoperability by Q3 2025, and require TPAP integration. Urgent system upgrades needed for PPI issuers.",
        "tasks": [
            {"id": "TASK-018", "description": "Upgrade PPI system to support ₹2L wallet limits", "assigned_department": "IT & Cybersecurity", "status": "in_progress", "due_date": "2025-02-28", "priority": "critical"},
            {"id": "TASK-019", "description": "Implement wallet interoperability with UPI/IMPS", "assigned_department": "IT & Cybersecurity", "status": "assigned", "due_date": "2025-06-30", "priority": "high"},
            {"id": "TASK-020", "description": "Update PPI T&C and customer communication", "assigned_department": "Retail Banking", "status": "draft", "due_date": "2025-03-15", "priority": "medium"},
        ]
    },
]


def load_circulars_from_files():
    """
    Load circulars from data/processed_circulars/*.json.
    Falls back to MOCK_CIRCULARS when the directory is empty or missing.
    Fields required by the API (tasks, status, etc.) are defaulted if absent.
    """
    processed_dir = Path(__file__).parent.parent / "data" / "processed_circulars"
    if not processed_dir.exists():
        return MOCK_CIRCULARS

    json_files = sorted(processed_dir.glob("*.json"))
    if not json_files:
        return MOCK_CIRCULARS

    # Build a lookup of existing mock IDs so we can merge tasks/status from them
    mock_by_id = {c["id"]: c for c in MOCK_CIRCULARS}

    circulars = []
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                raw = json.load(f)

            cid = raw.get("id", json_file.stem)

            # If a mock entry exists for this ID, use its tasks/status so the
            # UI task-tracking features keep working; otherwise use defaults.
            mock = mock_by_id.get(cid, {})

            circular = {
                "id":          cid,
                "title":       raw.get("title", mock.get("title", "RBI Circular")),
                "date_issued": raw.get("date_issued", mock.get("date_issued", "")),
                "category":    raw.get("category", mock.get("category", "Regulatory")),
                "severity":    raw.get("severity", mock.get("severity", "medium")),
                "status":      mock.get("status", raw.get("status", "draft")),
                "content":     raw.get("content", mock.get("content", "")),
                "ai_summary":  raw.get("ai_summary", mock.get("ai_summary", "")),
                "tasks":       mock.get("tasks", raw.get("tasks", [])),
            }
            circulars.append(circular)

        except Exception as e:
            print(f"Warning: could not load {json_file.name}: {e}")

    # Append any mock circulars whose IDs are not present in the processed files
    loaded_ids = {c["id"] for c in circulars}
    for mock in MOCK_CIRCULARS:
        if mock["id"] not in loaded_ids:
            circulars.append(mock)

    return circulars if circulars else MOCK_CIRCULARS


CIRCULARS = load_circulars_from_files()

AGENT_LOGS = [
    {"id": "LOG-001", "timestamp": "2025-01-15T09:12:34", "agent": "SupervisorAgent", "action": "Circular detected", "circular_id": "RBI/2025/002", "status": "success", "message": "New circular RBI/2025/002 detected on RBI website. Initiating parsing pipeline."},
    {"id": "LOG-002", "timestamp": "2025-01-15T09:12:41", "agent": "CircularParserAgent", "action": "Parsing circular", "circular_id": "RBI/2025/002", "status": "success", "message": "Extracted 3 compliance tasks from circular. Confidence: 94.2%"},
    {"id": "LOG-003", "timestamp": "2025-01-15T09:12:55", "agent": "TaskRouterAgent", "action": "Department assignment", "circular_id": "RBI/2025/002", "status": "success", "message": "Tasks routed: IT & Cybersecurity (2), Retail Banking (1). Routing confidence: 91.5%"},
    {"id": "LOG-004", "timestamp": "2025-01-15T09:13:02", "agent": "ValidatorAgent", "action": "Validation queued", "circular_id": "RBI/2025/002", "status": "pending", "message": "3 tasks queued for validation. Awaiting department acknowledgment."},
    {"id": "LOG-005", "timestamp": "2025-01-14T14:30:00", "agent": "SupervisorAgent", "action": "Circular detected", "circular_id": "RBI/2025/001", "status": "success", "message": "New circular RBI/2025/001 detected. Green deposit framework."},
    {"id": "LOG-006", "timestamp": "2025-01-14T14:30:12", "agent": "CircularParserAgent", "action": "Parsing circular", "circular_id": "RBI/2025/001", "status": "success", "message": "Extracted 3 compliance tasks. Novel category: Green Finance."},
    {"id": "LOG-007", "timestamp": "2025-01-10T11:20:00", "agent": "ValidatorAgent", "action": "Validation complete", "circular_id": "RBI/2024/004", "status": "success", "message": "All 3 tasks validated for RBI/2024/004. Circular marked complete."},
    {"id": "LOG-008", "timestamp": "2025-01-10T11:19:45", "agent": "ValidatorAgent", "action": "Evidence collected", "circular_id": "RBI/2024/004", "status": "success", "message": "CBS update logs and UAT reports collected as evidence for TASK-012, TASK-013."},
]

ALERTS = [
    {"id": "ALERT-001", "type": "deadline", "severity": "critical", "title": "TASK-002 Due in 5 days", "message": "CKYC Registry integration for RBI/2024/001 is due on 2025-02-08. Status: Assigned.", "timestamp": "2025-01-15T08:00:00", "read": False, "circular_id": "RBI/2024/001"},
    {"id": "ALERT-002", "type": "new_circular", "severity": "high", "title": "New RBI Circular Published", "message": "RBI/2025/002 on PPI amendments requires urgent action. 1 critical task identified.", "timestamp": "2025-01-15T09:12:34", "read": False, "circular_id": "RBI/2025/002"},
    {"id": "ALERT-003", "type": "overdue", "severity": "critical", "title": "TASK-001 Overdue", "message": "KYC forms update for RBI/2024/001 is overdue by 3 days.", "timestamp": "2025-01-15T07:00:00", "read": False, "circular_id": "RBI/2024/001"},
    {"id": "ALERT-004", "type": "validation", "severity": "medium", "title": "RBI/2024/004 Fully Compliant", "message": "All tasks for IRAC Prudential Norms circular have been validated. Circular closed.", "timestamp": "2025-01-10T11:20:00", "read": True, "circular_id": "RBI/2024/004"},
    {"id": "ALERT-005", "type": "agent", "severity": "low", "title": "Agent Pipeline Healthy", "message": "All 4 agents (Supervisor, Parser, Router, Validator) running normally. Last scan: 2 mins ago.", "timestamp": "2025-01-15T09:10:00", "read": True, "circular_id": None},
]

# ─── Routes ──────────────────────────────────────────────────────────

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    all_tasks = [t for c in CIRCULARS for t in c["tasks"]]
    total = len(all_tasks)
    complete = sum(1 for t in all_tasks if t["status"] == "complete")
    in_progress = sum(1 for t in all_tasks if t["status"] == "in_progress")
    overdue = 2
    compliance_rate = round((complete / total) * 100, 1)
    return {
        "total_circulars": len(CIRCULARS),
        "active_circulars": sum(1 for c in CIRCULARS if c["status"] != "complete"),
        "total_tasks": total,
        "complete_tasks": complete,
        "in_progress_tasks": in_progress,
        "overdue_tasks": overdue,
        "compliance_rate": compliance_rate,
        "critical_alerts": sum(1 for a in ALERTS if a["severity"] == "critical" and not a["read"]),
        "agent_status": "healthy",
        "last_scan": "2025-01-15T09:10:00",
    }

@app.get("/api/circulars")
def list_circulars(status: Optional[str] = None, severity: Optional[str] = None):
    result = CIRCULARS
    if status:
        result = [c for c in result if c["status"] == status]
    if severity:
        result = [c for c in result if c["severity"] == severity]
    return {"circulars": [{**c, "task_count": len(c["tasks"]), "completed_tasks": sum(1 for t in c["tasks"] if t["status"] == "complete")} for c in result]}

@app.get("/api/circulars/{circular_id:path}")
def get_circular(circular_id: str):
    """Get a specific circular by ID."""
    # Decode URL-encoded ID (RBI%2F2024%2F001 → RBI/2024/001)
    circular_id = unquote(circular_id)
    
    print(f"DEBUG: Looking for circular_id: {circular_id}")
    print(f"DEBUG: Available IDs: {[c['id'] for c in CIRCULARS]}")
    
    # Search in CIRCULARS directly
    for circular in CIRCULARS:
        print(f"DEBUG: Comparing '{circular['id']}' with '{circular_id}'")
        if circular['id'] == circular_id:
            return circular
    
    raise HTTPException(status_code=404, detail=f"Circular not found: {circular_id}")

@app.get("/api/tasks")
def list_tasks(status: Optional[str] = None, department: Optional[str] = None):
    all_tasks = []
    for c in CIRCULARS:
        for t in c["tasks"]:
            task = {**t, "circular_id": c["id"], "circular_title": c["title"]}
            if (not status or task["status"] == status) and (not department or task["assigned_department"] == department):
                all_tasks.append(task)
    return {"tasks": all_tasks}

@app.post("/api/tasks/{task_id}/validate")
def validate_task(task_id: str):
    for c in CIRCULARS:
        for t in c["tasks"]:
            if t["id"] == task_id:
                t["status"] = "validated"
                return {"task_id": task_id, "status": "verified", "evidence": f"System validation passed at {datetime.now().isoformat()}"}
    raise HTTPException(404, "Task not found")

@app.get("/api/departments")
def list_departments():
    result = []
    for dept in DEPARTMENTS:
        all_tasks = [t for c in CIRCULARS for t in c["tasks"] if t["assigned_department"] == dept["name"]]
        completed = sum(1 for t in all_tasks if t["status"] in ["complete", "validated"])
        result.append({
            **dept,
            "total_tasks": len(all_tasks),
            "completed": completed,
            "pending": len(all_tasks) - completed,
            "completion_rate": round((completed / len(all_tasks) * 100), 1) if all_tasks else 0,
        })
    return {"departments": result}

@app.get("/api/departments/{dept_id}/status")
def dept_status(dept_id: str):
    dept = next((d for d in DEPARTMENTS if d["id"] == dept_id), None)
    if not dept:
        raise HTTPException(404, "Department not found")
    all_tasks = [t for c in CIRCULARS for t in c["tasks"] if t["assigned_department"] == dept["name"]]
    completed = sum(1 for t in all_tasks if t["status"] in ["complete", "validated"])
    return {**dept, "total_tasks": len(all_tasks), "completed": completed, "pending": len(all_tasks) - completed, "completion_rate": round((completed / len(all_tasks) * 100), 1) if all_tasks else 0}

@app.get("/api/agents/logs")
def get_agent_logs():
    return {"logs": AGENT_LOGS}

@app.get("/api/agents/status")
def agent_status():
    return {
        "agents": [
            {"name": "SupervisorAgent", "status": "running", "last_run": "2025-01-15T09:12:34", "circulars_processed": 6, "uptime": "99.8%"},
            {"name": "CircularParserAgent", "status": "running", "last_run": "2025-01-15T09:12:41", "tasks_extracted": 20, "uptime": "99.5%"},
            {"name": "TaskRouterAgent", "status": "running", "last_run": "2025-01-15T09:12:55", "routing_accuracy": "91.5%", "uptime": "99.9%"},
            {"name": "ValidatorAgent", "status": "idle", "last_run": "2025-01-15T09:13:02", "validations_done": 8, "uptime": "98.7%"},
        ]
    }

@app.get("/api/alerts")
def get_alerts():
    return {"alerts": ALERTS}

@app.put("/api/alerts/{alert_id}/read")
def mark_alert_read(alert_id: str):
    for a in ALERTS:
        if a["id"] == alert_id:
            a["read"] = True
            return {"success": True}
    raise HTTPException(404, "Alert not found")

@app.get("/api/analytics/compliance-trend")
def compliance_trend():
    months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
    return {"trend": [{"month": m, "rate": r} for m, r in zip(months, [52, 61, 67, 74, 79, 83])]}

@app.get("/api/analytics/category-distribution")
def category_distribution():
    categories = {}
    for c in CIRCULARS:
        categories[c["category"]] = categories.get(c["category"], 0) + 1
    return {"distribution": [{"category": k, "count": v} for k, v in categories.items()]}

@app.get("/api/analytics/department-performance")
def dept_performance():
    result = []
    for dept in DEPARTMENTS:
        all_tasks = [t for c in CIRCULARS for t in c["tasks"] if t["assigned_department"] == dept["name"]]
        completed = sum(1 for t in all_tasks if t["status"] in ["complete", "validated"])
        if all_tasks:
            result.append({"department": dept["name"], "total": len(all_tasks), "completed": completed, "rate": round(completed/len(all_tasks)*100, 1)})
    return {"performance": result}

@app.post("/api/agents/trigger-scan")
def trigger_scan():
    return {"status": "triggered", "message": "Agent pipeline scan initiated. Results will appear in 30-60 seconds.", "scan_id": str(uuid.uuid4())}
