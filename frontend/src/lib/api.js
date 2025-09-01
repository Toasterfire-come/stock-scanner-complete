export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function withApiPrefix(path) {
  // Always prefer /api prefix per ingress rules
  if (path.startsWith('/api')) return path;
  return `/api${path.startsWith('/') ? '' : '/'}${path}`;
}

export async function apiFetch(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? 15000);
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const url = `${BACKEND_URL}${withApiPrefix(path)}`;
  try {
    const res = await fetch(url, {
      method: options.method || 'GET',
      headers,
      credentials: 'include',
      signal: controller.signal,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await res.json() : await res.text();
    if (!res.ok) {
      throw new Error((isJson ? (data.error || data.message) : data) || `HTTP ${res.status}`);
    }
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error: error.message || 'Network error' };
  } finally {
    clearTimeout(timeout);
  }
}

export async function tryHealth() {
  return apiFetch('/health/');
}

// Some endpoints exist without /api prefix in docs (e.g., /endpoint-status/). Try both.
export async function getEndpointStatus() {
  // First try /api/endpoint-status/
  const first = await apiFetch('/endpoint-status/');
  if (first.ok) return first;
  // Fallback to non-prefixed (in case backend exposes it only there)
  const controller = new AbortController();
  const url = `${BACKEND_URL}/endpoint-status/`;
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' }, signal: controller.signal });
    const data = await res.json();
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: first.error || e.message };
  }
}

export const endpoints = {
  auth: {
    login: (body) => apiFetch('/auth/login/', { method: 'POST', body }),
    logout: () => apiFetch('/auth/logout/', { method: 'POST' }),
    signup: (body) => apiFetch('/auth/signup/', { method: 'POST', body }), // may 404, handle gracefully
    forgotPassword: (body) => apiFetch('/auth/forgot-password/', { method: 'POST', body }),
    resetPassword: (body) => apiFetch('/auth/reset-password/', { method: 'POST', body }),
    verifyEmail: (token) => apiFetch(`/auth/verify-email/?token=${encodeURIComponent(token)}`),
  },
  user: {
    profileGet: () => apiFetch('/user/profile/'),
    profileUpdate: (body) => apiFetch('/user/profile/', { method: 'POST', body }),
    changePassword: (body) => apiFetch('/user/change-password/', { method: 'POST', body }),
    notificationGet: () => apiFetch('/user/notification-settings/'),
    notificationUpdate: (body) => apiFetch('/user/notification-settings/', { method: 'POST', body }),
    billingHistory: (params) => apiFetch(`/user/billing-history/${buildQuery(params)}`),
  },
  billing: {
    currentPlan: () => apiFetch('/billing/current-plan/'),
    changePlan: (body) => apiFetch('/billing/change-plan/', { method: 'POST', body }),
    stats: () => apiFetch('/billing/stats/'),
    downloadInvoice: (invoiceId) => apiFetch(`/billing/download/${invoiceId}/`),
    validateDiscount: (code) => apiFetch('/revenue/validate-discount/', { method: 'POST', body: { code } }),
    applyDiscount: (code, amount) => apiFetch('/revenue/apply-discount/', { method: 'POST', body: { code, amount } }),
    paypalCreate: (plan) => apiFetch('/paypal/create-order', { method: 'POST', body: { plan } }),
    paypalCapture: (id) => apiFetch(`/paypal/capture-order/${id}`, { method: 'POST' }),
  },
  stocks: {
    list: (params) => apiFetch(`/stocks/${buildQuery(params)}`),
    detail: (ticker) => apiFetch(`/stock/${encodeURIComponent(ticker)}/`),
    realtime: (ticker) => apiFetch(`/realtime/${encodeURIComponent(ticker)}/`),
    trending: () => apiFetch('/trending/'),
    marketStats: () => apiFetch('/market-stats/'),
    filter: (params) => apiFetch(`/filter/${buildQuery(params)}`),
    search: (q) => apiFetch(`/search/?q=${encodeURIComponent(q)}`),
  },
  news: {
    feed: (params) => apiFetch(`/news/feed/${buildQuery(params)}`),
    markRead: (body) => apiFetch('/news/mark-read/', { method: 'POST', body }),
    markClicked: (body) => apiFetch('/news/mark-clicked/', { method: 'POST', body }),
    preferences: (body) => apiFetch('/news/preferences/', { method: 'POST', body }),
    syncPortfolio: () => apiFetch('/news/sync-portfolio/', { method: 'POST' }),
  },
  subscriptions: {
    subscribe: (body) => apiFetch('/subscription/', { method: 'POST', body }),
    wordpressStocks: (params) => apiFetch(`/wordpress/stocks/${buildQuery(params)}`),
    wordpressNews: (params) => apiFetch(`/wordpress/news/${buildQuery(params)}`),
    wordpressAlerts: (params) => apiFetch(`/wordpress/alerts/${buildQuery(params)}`),
  },
};

function buildQuery(params) {
  if (!params) return '';
  const pairs = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && `${v}` !== '');
  if (!pairs.length) return '';
  const qs = new URLSearchParams();
  for (const [k, v] of pairs) qs.append(k, v);
  return `?${qs.toString()}`;
}