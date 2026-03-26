/* Service Worker — Gelateria Sistema (offline-first shell) */

const CACHE_NAME = "gelateria-v2";
const SHELL_ASSETS = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json",
];

// Install: pre-cache shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

// Activate: remove old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: serve shell from cache; API calls network-first with fallback
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // API calls — network first, no cache
  if (url.pathname.startsWith("/cmd") || url.pathname.startsWith("/health")) {
    return; // let browser handle normally
  }

  // Shell assets — cache first
  event.respondWith(
    caches.match(event.request).then(
      (cached) => cached || fetch(event.request).catch(() => caches.match("/index.html"))
    )
  );
});
