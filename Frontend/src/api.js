const API_BASE = "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
  } catch {
    throw new Error("Cannot connect to the backend. Start FastAPI at http://127.0.0.1:8000 and check the database connection.");
  }
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = payload && typeof payload === "object" ? payload.detail : null;
    const message = Array.isArray(detail) ? detail.map((item) => item.msg || JSON.stringify(item)).join(", ") : detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return payload;
}
export const getDashboardStatistics = () => request("/statistics/dashboard");
export const getFraudDistribution = () => request("/analytics/fraud-distribution");
export const getRiskDistribution = () => request("/analytics/risk-distribution");
export const getRecentActivity = (limit = 5) => request(`/analytics/recent-activity?limit=${encodeURIComponent(limit)}`);
export const analyzeFraudMessage = (message) => request("/frauds/analyze", { method: "POST", body: JSON.stringify({ message }) });
export const getFraudCases = (search = "") => {
  const query = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : "";
  return request(`/frauds/${query}`);
};
export const getHistory = ({ page = 1, limit = 10, search = "", risk_level = "" } = {}) => {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (search.trim()) params.set("search", search.trim());
  if (risk_level) params.set("risk_level", risk_level);
  return request(`/history/?${params.toString()}`);
};
