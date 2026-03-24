/**
 * Service Worker — Gelateria Sistema
 * Provides offline support with a cache-first strategy for static assets
 * and a network-first strategy for API calls.
 */

const CACHE_NAME = "gelateria-v1";
const STATIC_ASSETS = ["/index.html", "/style.css", "/script.js", "/manifest.json"];

// ── Install: pre-cache static assets ────────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ── Activate: clean up old caches ───────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch: cache-first for static, network-first for API ────────────────────
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Network-first for API requests
  if (url.pathname.startsWith("/cmd") || url.pathname.startsWith("/health")) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(
          JSON.stringify({ resposta: "[Offline] Sem conexão com o servidor." }),
          { headers: { "Content-Type": "application/json" } }
        )
      )
    );
    return;
  }

  // Cache-first for static assets
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
