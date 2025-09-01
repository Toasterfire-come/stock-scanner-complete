import axios from "axios";

const BASE_URL = (import.meta?.env?.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || "").trim();
if (!BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn("REACT_APP_BACKEND_URL is not set. API calls will fail.");
}

export const API_ROOT = `${BASE_URL}/api`;

export const api = axios.create({
  baseURL: API_ROOT,
  withCredentials: false,
});

// attach token if present
api.interceptors.request.use((config) => {
  try {
    const token = window.localStorage.getItem("rts_token");
    if (token) {
      // Our backend expects Authorization string; pass via query param as fallback
      config.params = config.params || {};
      config.params.authorization = `Bearer ${token}`;
    }
  } catch (e) {
    // ignore
  }
  return config;
});

export async function pingHealth() {
  const { data } = await api.get("/health/");
  return data;
}

export async function listStocks(params = {}) {
  const { data } = await api.get("/stocks/", { params });
  return data;
}

export async function getStock(ticker) {
  const { data } = await api.get(`/stock/${encodeURIComponent(ticker)}/`);
  return data;
}

export async function searchStocks(q) {
  const { data } = await api.get("/search/", { params: { q } });
  return data;
}

export async function getTrending() {
  const { data } = await api.get("/trending/");
  return data;
}

export async function getMarketStats() {
  const { data } = await api.get("/market-stats/");
  return data;
}

export async function login(username, password) {
  const { data } = await api.post("/auth/login/", { username, password });
  return data;
}

export async function getProfile() {
  const { data } = await api.get("/user/profile/");
  return data;
}

export async function getWatchlist() {
  const { data } = await api.get("/watchlist/");
  return data;
}

export async function addWatchlist(symbol, opts = {}) {
  const { data } = await api.post("/watchlist/add/", { symbol, ...opts });
  return data;
}

export async function deleteWatchlist(id) {
  const { data } = await api.delete(`/watchlist/${id}/`);
  return data;
}

export async function getPortfolio() {
  const { data } = await api.get("/portfolio/");
  return data;
}

export async function addPortfolio(payload) {
  const { data } = await api.post("/portfolio/add/", payload);
  return data;
}

export async function deletePortfolio(id) {
  const { data } = await api.delete(`/portfolio/${id}/`);
  return data;
}

export async function alertsMeta() {
  const { data } = await api.get("/alerts/create/");
  return data;
}

export async function createAlert(payload) {
  const { data } = await api.post("/alerts/create/", payload);
  return data;
}

export async function revenueInitialize() {
  const { data } = await api.post("/revenue/initialize-codes/");
  return data;
}

export async function revenueValidate(code) {
  const { data } = await api.post("/revenue/validate-discount/", { code });
  return data;
}

export async function revenueApply(code, amount) {
  const { data } = await api.post("/revenue/apply-discount/", { code, amount });
  return data;
}