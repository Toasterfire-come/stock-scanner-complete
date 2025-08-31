import axios from "axios";

const BASE = process.env.REACT_APP_BACKEND_URL;
if (!BASE) {
  // eslint-disable-next-line no-console
  console.warn("REACT_APP_BACKEND_URL is not set. API calls will fail.");
}

export const api = axios.create({
  baseURL: `${BASE}/api`,
  headers: { "Content-Type": "application/json" },
});

export function getHealth() {
  return api.get("/health/");
}

export function getTrending() {
  return api.get("/trending/");
}

export function getAllowedAlertSchema() {
  return api.get("/alerts/create/");
}

export function createAlert(payload) {
  return api.post("/alerts/create/", payload);
}

export function listAlerts(params) {
  // wordpress proxy for alerts
  return api.get("/wordpress/alerts/", { params });
}