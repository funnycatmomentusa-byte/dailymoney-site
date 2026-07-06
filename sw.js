const CACHE_NAME = 'dailymoney-v1';
const ASSETS = [
  '/',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/js/articles.js',
];

// Install: cache assets
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// Activate: clean old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
});

// Fetch: network-first, fallback to cache
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});

// Push notification
self.addEventListener('push', (e) => {
  const data = e.data.json();
  const options = {
    body: data.body || 'Artikel baru di DailyMoney',
    icon: '/assets/icons/icon-192.png',
    badge: '/assets/icons/badge.png',
    data: { url: data.url || '/' }
  };
  e.waitUntil(
    self.registration.showNotification(data.title || 'DailyMoney', options)
  );
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data.url));
});
