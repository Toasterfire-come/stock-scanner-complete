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

export function getHealth() { return api.get("/health/"); }
export function getTrending() { return api.get("/trending/"); }

// Alerts
export function getAllowedAlertSchema() { return api.get("/alerts/create/"); }
export function createAlert(payload) { return api.post("/alerts/create/", payload); }
export function listAlerts(params) { return api.get("/wordpress/alerts/", { params }); }

// Portfolio
export function getPortfolio() { return api.get("/portfolio/"); }
export function addHolding(payload) { return api.post("/portfolio/add/", payload); }
export function deleteHolding(id) { return api.delete(`/portfolio/${id}/`); }

// Watchlist
export function getWatchlist() { return api.get("/watchlist/"); }
export function addWatchlistItem(payload) { return api.post("/watchlist/add/", payload); }
export function deleteWatchlistItem(id) { return api.delete(`/watchlist/${id}/`); }