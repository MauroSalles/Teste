/**
 * sw.js — Service Worker for Gelateria Sistema (PWA)
 * Strategy:
 *   - Cache-first for static assets (CSS, JS, images)
 *   - Network-first for API calls
 *   - Offline fallback page for navigation requests
 */

const CACHE_NAME    = 'gelateria-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/css/animations.css',
  '/js/api.js',
  '/js/auth.js',
  '/js/app.js',
  '/js/terminal.js',
  '/js/admin.js',
  '/manifest.json',
];

// ── Install ───────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ── Activate ──────────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Network-first for API and auth requests
  if (url.pathname.startsWith('/api') || url.pathname === '/cmd' || url.pathname === '/health') {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Cache-first for static assets
  event.respondWith(cacheFirst(event.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (_) {
    return new Response('<h1>Offline</h1><p>Sem conexão com a internet.</p>', {
      headers: { 'Content-Type': 'text/html' },
    });
  }
}

async function networkFirst(request) {
  try {
    return await fetch(request);
  } catch (_) {
    const cached = await caches.match(request);
    return cached || new Response(JSON.stringify({ error: 'Sem conexão.' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
