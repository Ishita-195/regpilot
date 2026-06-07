const BASE = "http://localhost:8000/api";

async function req(path) {
  try {
    const res = await fetch(`${BASE}${path}`);
    return res.json();
  } catch {
    return null;
  }
}

async function post(path, body) {
  try {
    const res = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    return res.json();
  } catch {
    return null;
  }
}

async function put(path) {
  try {
    const res = await fetch(`${BASE}${path}`, { method: "PUT" });
    return res.json();
  } catch {
    return null;
  }
}

export const api = {
  getDashboardStats: () => req("/dashboard/stats"),
  getCirculars: (params = "") => req(`/circulars${params}`),
  getCircular: (id) => req(`/circulars/${id}`),
  getTasks: (params = "") => req(`/tasks${params}`),
  validateTask: (taskId) => post(`/tasks/${taskId}/validate`),
  getDepartments: () => req("/departments"),
  getDepartmentStatus: (id) => req(`/departments/${id}/status`),
  getAgentLogs: () => req("/agents/logs"),
  getAgentStatus: () => req("/agents/status"),
  getAlerts: () => req("/alerts"),
  markAlertRead: (id) => put(`/alerts/${id}/read`),
  getComplianceTrend: () => req("/analytics/compliance-trend"),
  getCategoryDistribution: () => req("/analytics/category-distribution"),
  getDeptPerformance: () => req("/analytics/department-performance"),
  triggerScan: () => post("/agents/trigger-scan"),
};
