/**
 * api.js — Centralised HTTP client for the Gelateria API.
 * All fetch calls go through here so auth headers are applied consistently.
 */

const API_BASE = (() => {
  // 1. Explicit override set by the deployment (e.g. Vercel env var injected into window)
  if (window.API_URL) return window.API_URL;
  // 2. In production the SPA and API share the same origin (Vercel rewrites /api/* to backend)
  if (location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
    return window.location.origin;
  }
  // 3. Local development: backend runs on port 5000 regardless of front-end dev server port
  return 'http://localhost:5000';
})();

// ── Token storage ─────────────────────────────────────────────────────────
const TokenStore = {
  get access()  { return localStorage.getItem('access_token'); },
  get refresh() { return localStorage.getItem('refresh_token'); },
  set(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// ── Core request helper ───────────────────────────────────────────────────
async function apiRequest(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

  if (TokenStore.access) {
    headers['Authorization'] = `Bearer ${TokenStore.access}`;
  }

  let resp = await fetch(url, { ...options, headers });

  // Auto-refresh on 401 if we have a refresh token
  if (resp.status === 401 && TokenStore.refresh) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${TokenStore.access}`;
      resp = await fetch(url, { ...options, headers });
    }
  }

  if (!resp.ok) {
    let errMsg = `HTTP ${resp.status}`;
    try { errMsg = (await resp.json()).error || errMsg; } catch (_) {}
    throw new ApiError(errMsg, resp.status);
  }

  if (resp.status === 204) return null;
  return resp.json();
}

async function tryRefresh() {
  try {
    const body = JSON.stringify({ refresh_token: TokenStore.refresh });
    const resp = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    if (!resp.ok) { TokenStore.clear(); return false; }
    const data = await resp.json();
    TokenStore.set(data.access_token, data.refresh_token);
    return true;
  } catch (_) {
    TokenStore.clear();
    return false;
  }
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// ── API endpoints ─────────────────────────────────────────────────────────
const Api = {
  // Auth
  auth: {
    login:    (email, senha) => apiRequest('/api/auth/login',    { method: 'POST', body: JSON.stringify({ email, senha }) }),
    register: (nome, email, senha) => apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify({ nome, email, senha }) }),
    logout:   (refresh_token) => apiRequest('/api/auth/logout',  { method: 'POST', body: JSON.stringify({ refresh_token }) }),
    me:       () => apiRequest('/api/auth/me'),
  },
  // Sabores
  sabores: {
    list:    ()                => apiRequest('/api/sabores'),
    create:  (nome, preco)     => apiRequest('/api/sabores',   { method: 'POST',   body: JSON.stringify({ nome, preco }) }),
    update:  (id, preco)       => apiRequest(`/api/sabores/${id}`, { method: 'PUT', body: JSON.stringify({ preco }) }),
    remove:  (id)              => apiRequest(`/api/sabores/${id}`, { method: 'DELETE' }),
  },
  // Pedidos
  pedidos: {
    list:   ()                  => apiRequest('/api/pedidos'),
    create: (sabor, quantidade) => apiRequest('/api/pedidos', { method: 'POST', body: JSON.stringify({ sabor, quantidade }) }),
  },
  // Estoque
  estoque: {
    list:   ()                       => apiRequest('/api/estoque'),
    set:    (sabor_id, quantidade)   => apiRequest(`/api/estoque/${sabor_id}`, { method: 'PUT', body: JSON.stringify({ quantidade }) }),
  },
  // Dashboard
  dashboard: {
    get: () => apiRequest('/api/dashboard'),
  },
  // Legacy terminal
  cmd: (comando) => apiRequest('/cmd', { method: 'POST', body: JSON.stringify({ comando }) }),

  // Health
  health: () => apiRequest('/health'),
};

window.Api = Api;
window.TokenStore = TokenStore;
window.ApiError = ApiError;
