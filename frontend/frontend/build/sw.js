
const CACHE_NAME = 'trade-scan-pro-v1.0.3';
const urlsToCache = [
  '/',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  // Activate updated SW immediately
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching app shell');
        return cache.addAll(urlsToCache.map(url => new Request(url, {credentials: 'same-origin'})));
      })
      .catch(error => {
        console.error('Cache addAll failed:', error);
      })
  );
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') {
    return;
  }
  
  // Bypass service worker for cross-origin requests (e.g., Google Fonts, analytics)
  try {
    const requestUrl = new URL(event.request.url);
    if (requestUrl.origin !== self.location.origin) {
      return; // Let the browser handle it directly
    }
  } catch (_) {}
  
  // Skip caching for API requests
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request).catch(() => {
          // Return offline page or safe empty response on failure
          if (event.request.destination === 'document') {
            return caches.match('/');
          }
          return new Response('', { status: 504, statusText: 'Gateway Timeout' });
        });
      })
  );
});
