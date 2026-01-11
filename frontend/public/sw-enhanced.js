/**
 * Enhanced Service Worker for MyCRM PWA
 * Includes background sync, push notifications, and offline support
 */

const CACHE_VERSION = 'v2';
const STATIC_CACHE = `mycrm-static-${CACHE_VERSION}`;
const API_CACHE = `mycrm-api-${CACHE_VERSION}`;
const IMAGE_CACHE = `mycrm-images-${CACHE_VERSION}`;

// Assets to precache
const PRECACHE_ASSETS = [
  '/',
  '/dashboard',
  '/contacts',
  '/leads',
  '/opportunities',
  '/offline.html',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// API routes that should work offline
const OFFLINE_API_ROUTES = [
  '/api/v1/contacts/',
  '/api/v1/leads/',
  '/api/v1/opportunities/',
  '/api/v1/tasks/',
];

// Install event - precache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return (
              cacheName.startsWith('mycrm-') &&
              cacheName !== STATIC_CACHE &&
              cacheName !== API_CACHE &&
              cacheName !== IMAGE_CACHE
            );
          })
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
  // Take control immediately
  self.clients.claim();
});

// Fetch event - handle requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle image requests
  if (request.destination === 'image') {
    event.respondWith(handleImageRequest(request));
    return;
  }

  // Handle static assets and pages
  event.respondWith(handleStaticRequest(request));
});

// Network-first strategy for API with cache fallback
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful GET requests for offline API routes
    if (networkResponse.ok && OFFLINE_API_ROUTES.some((route) => url.pathname.startsWith(route))) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch {
    // Try cache fallback
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'You are currently offline. This data will sync when you reconnect.',
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

// Cache-first strategy for images
async function handleImageRequest(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(IMAGE_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch {
    // Return placeholder image
    return caches.match('/icons/placeholder.png');
  }
}

// Stale-while-revalidate for static assets
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);

  // Start network request in background
  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        const cache = caches.open(STATIC_CACHE);
        cache.then((c) => c.put(request, networkResponse.clone()));
      }
      return networkResponse;
    })
    .catch(() => null);

  // Return cached response immediately, or wait for network
  if (cachedResponse) {
    return cachedResponse;
  }

  const networkResponse = await fetchPromise;
  if (networkResponse) {
    return networkResponse;
  }

  // Return offline page for navigation requests
  if (request.mode === 'navigate') {
    return caches.match('/offline.html');
  }

  return new Response('Offline', { status: 503 });
}

// Background sync for offline mutations
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncOfflineData());
  }
});

async function syncOfflineData() {
  // This will be handled by the frontend SyncService
  // Notify all clients to trigger sync
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({ type: 'SYNC_REQUIRED' });
  });
}

// Push notifications
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
      ...data.data,
    },
    actions: data.actions || [],
    tag: data.tag || 'default',
    renotify: data.renotify || false,
    requireInteraction: data.requireInteraction || false,
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const url = event.notification.data?.url || '/';
  const action = event.action;

  event.waitUntil(
    (async () => {
      // Handle action buttons
      if (action) {
        switch (action) {
          case 'view':
            await openUrl(url);
            break;
          case 'dismiss':
            // Just close notification
            break;
          case 'reply':
            // Open reply interface
            await openUrl(`${url}?action=reply`);
            break;
          default:
            await openUrl(url);
        }
      } else {
        // Default click - open the URL
        await openUrl(url);
      }
    })()
  );
});

async function openUrl(url) {
  const windowClients = await self.clients.matchAll({
    type: 'window',
    includeUncontrolled: true,
  });

  // Check if already open
  for (const client of windowClients) {
    if (client.url === url && 'focus' in client) {
      return client.focus();
    }
  }

  // Open new window
  if (self.clients.openWindow) {
    return self.clients.openWindow(url);
  }
}

// Handle notification close
self.addEventListener('notificationclose', (event) => {
  // Track notification dismissals for analytics
  const data = event.notification.data;
  if (data?.trackDismissal) {
    // Could send analytics event here
  }
});

// Message handler for client communication
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CACHE_URLS':
      event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => cache.addAll(payload.urls))
      );
      break;

    case 'CLEAR_CACHE':
      event.waitUntil(
        caches.keys().then((names) =>
          Promise.all(names.map((name) => caches.delete(name)))
        )
      );
      break;

    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_VERSION });
      break;
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'sync-contacts') {
    event.waitUntil(syncContacts());
  }
});

async function syncContacts() {
  // Fetch latest contacts for offline access
  try {
    const response = await fetch('/api/v1/contacts/?limit=100');
    if (response.ok) {
      const cache = await caches.open(API_CACHE);
      await cache.put('/api/v1/contacts/?limit=100', response);
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}
