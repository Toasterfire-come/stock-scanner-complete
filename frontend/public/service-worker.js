/**
 * Service Worker for Stock Scanner
 * Provides offline support and caching
 */

const CACHE_NAME = 'stock-scanner-v1';
const API_CACHE = 'stock-scanner-api-v1';
const API_URL = 'https://api.retailtradescanner.com';

// Files to cache for offline use
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache.map(url => new Request(url, {credentials: 'same-origin'})));
      })
      .catch(err => {
        console.error('Cache install failed:', err);
      })
  );
  // Skip waiting to activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all pages immediately
  self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle API requests
  if (url.origin === API_URL) {
    event.respondWith(
      networkFirstStrategy(request)
    );
    return;
  }
  
  // Handle static assets
  if (url.origin === location.origin) {
    event.respondWith(
      cacheFirstStrategy(request)
    );
    return;
  }
  
  // For everything else, try network
  event.respondWith(fetch(request));
});

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    // Update cache in background
    fetchAndCache(request, cache);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return offline page if available
    const offlineResponse = await cache.match('/offline.html');
    if (offlineResponse) {
      return offlineResponse;
    }
    throw error;
  }
}

// Network-first strategy for API calls
async function networkFirstStrategy(request) {
  const cache = await caches.open(API_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful GET requests to specific endpoints
    if (networkResponse.ok && shouldCacheAPIResponse(request.url)) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Try cache for API calls
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      console.log('Serving API response from cache:', request.url);
      return cachedResponse;
    }
    
    // Return error response
    return new Response(JSON.stringify({
      error: true,
      message: 'Network request failed and no cache available'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Determine if API response should be cached
function shouldCacheAPIResponse(url) {
  // Cache these endpoints for offline use
  const cacheableEndpoints = [
    '/api/stocks/',
    '/api/market-stats/',
    '/api/trending/',
    '/api/health/'
  ];
  
  return cacheableEndpoints.some(endpoint => url.includes(endpoint));
}

// Background fetch and cache update
async function fetchAndCache(request, cache) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response);
    }
  } catch (error) {
    // Ignore errors in background update
  }
}

// Listen for messages from the app
self.addEventListener('message', event => {
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
      })
    );
  }
});