// DailyMoney Security Note
// Security headers should be configured at CDN/reverse proxy level
// For GitHub Pages: Use Cloudflare for HSTS, CSP, and other headers
// Or configure via _headers file for Cloudflare Pages

// ============================================
// DailyMoney Service Worker — v2 (Network-First)
// ============================================
const CACHE_VERSION = 'dm-cache-v2';
const SHELL_URLS = [
  '/',
  '/en/',
  '/assets/css/style.css',
  '/id/index.html',
  '/en/index.html',
  '/404.html',
];

// ----- INSTALL: Pre-cache shell -----
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(function(cache) {
      return cache.addAll(SHELL_URLS);
    })
  );
  self.skipWaiting();
});

// ----- ACTIVATE: Clean old caches -----
self.addEventListener('activate', function(event) {
  event.waitUntil(
    Promise.all([
      caches.keys().then(function(cacheNames) {
        return Promise.all(
          cacheNames.filter(function(name) {
            return name !== CACHE_VERSION && name.startsWith('dm-cache');
          }).map(function(name) {
            return caches.delete(name);
          })
        );
      }),
      self.clients.claim()
    ])
  );
});

// ----- FETCH: Network-first for HTML + JS; Cache-first for static assets -----
self.addEventListener('fetch', function(event) {
  var url = new URL(event.request.url);
  var isPage = url.pathname === '/' || url.pathname === '/en/' || url.pathname.endsWith('.html');
  var isScript = url.pathname.endsWith('.js');
  var isStyle = url.pathname.endsWith('.css');
  var isImage = url.pathname.match(/\.(png|jpg|jpeg|gif|svg|ico|webp)$/i);

  // Network First for HTML pages and JS — ensures fresh content
  if (isPage || isScript) {
    event.respondWith(
      fetch(event.request)
        .then(function(response) {
          if (response && response.ok) {
            var clone = response.clone();
            caches.open(CACHE_VERSION).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        })
        .catch(function() {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache First for CSS, images, and other static assets
  if (isStyle || isImage) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        return cached || fetch(event.request).then(function(response) {
          if (response && response.ok) {
            var clone = response.clone();
            caches.open(CACHE_VERSION).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Everything else: network-only (don't cache API calls, _price_data.json, etc.)
  event.respondWith(fetch(event.request));
});
