const CACHE_NAME = 'signvalid-v7';
const OFFLINE_URL = '/';

const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-maskable-192.png',
  '/static/icon-maskable-512.png'
];

// Pre-cache core shell during installation
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('Pre-caching shell warning:', err);
      });
    })
  );
  self.skipWaiting();
});

// Purge obsolete caches on activation
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Offline fallback HTML generator (never shows a blank screen)
function getOfflineFallbackHtml() {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SignValid — Connecting to Server</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #fff; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; text-align: center; }
    .card { background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 36px 24px; max-width: 380px; width: 100%; box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
    .spinner { width: 44px; height: 44px; border: 4px solid rgba(16, 185, 129, 0.2); border-top-color: #10b981; border-radius: 50%; animation: spin 0.9s linear infinite; margin: 0 auto 18px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    h2 { font-size: 19px; font-weight: 800; margin: 0 0 10px; color: #fff; }
    p { font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 0 0 24px; }
    .btn { background: #10b981; color: #064e3b; font-weight: 700; border: none; padding: 13px 26px; border-radius: 14px; font-size: 14px; cursor: pointer; text-decoration: none; display: inline-block; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3); }
    .btn:active { transform: scale(0.97); }
  </style>
</head>
<body>
  <div class="card">
    <div class="spinner"></div>
    <h2>Connecting to Server...</h2>
    <p>SignValid server is waking up (takes ~25 seconds on free cloud tier). Tap below or wait a moment.</p>
    <button class="btn" onclick="window.location.reload()">Retry Connection</button>
  </div>
</body>
</html>`;
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

// Stale-While-Revalidate Navigation for 0ms Instant Mobile Load
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // 1. Navigation requests (HTML pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.match(OFFLINE_URL).then((cachedResponse) => {
        // Fetch from network with timeout
        const networkFetch = fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone)).catch(() => {});
            }
            return networkResponse;
          })
          .catch(() => null);

        // If we have a cached version, return it INSTANTLY (0ms mobile launch!)
        if (cachedResponse) {
          // Revalidate in background
          networkFetch.catch(() => {});
          return cachedResponse;
        }

        // If not cached yet, wait for network or fallback
        return networkFetch.then((res) => res || getOfflineFallbackHtml());
      }).catch(() => getOfflineFallbackHtml())
    );
    return;
  }

  // 2. CDNs (Tailwind, Lucide, Fonts) & Images
  if (url.origin !== location.origin || url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone)).catch(() => {});
            }
            return networkResponse;
          })
          .catch(() => new Response('', { status: 408 }));
      })
    );
    return;
  }

  // 3. Default network-first
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
