/**
 * Service Worker for Weather App PWA
 *
 * Caching strategies:
 * - App shell (HTML, CSS, JS): Cache-first with network fallback
 * - Weather API data: Network-first with cache fallback (stale-while-revalidate)
 * - Static assets: Cache-first
 */

const CACHE_VERSION = 'v1';
const STATIC_CACHE = `weather-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `weather-dynamic-${CACHE_VERSION}`;

// App shell resources to cache immediately
const APP_SHELL = [
    '/static/css/app.css',
    '/static/js/weather-api.js',
    '/static/js/state-manager.js',
    '/static/js/weather-app.js',
    '/static/manifest.json',
    '/static/icons/icon-192.svg',
    '/static/icons/icon-512.svg'
];

// External resources to cache
const EXTERNAL_RESOURCES = [
    'https://cdn.jsdelivr.net/npm/@fluentui/web-components@2.6.0/dist/web-components.min.js',
    'https://cdn.jsdelivr.net/npm/@fluentui/tokens@1.0.0-alpha.27/global.css'
];

/**
 * Install event - cache app shell
 */
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');

    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching app shell');
                // Cache app shell resources
                return cache.addAll(APP_SHELL);
            })
            .then(() => {
                // Cache external resources separately (may fail due to CORS)
                return caches.open(STATIC_CACHE).then((cache) => {
                    return Promise.allSettled(
                        EXTERNAL_RESOURCES.map((url) =>
                            cache.add(url).catch((err) => {
                                console.warn(`[SW] Failed to cache external resource: ${url}`, err);
                            })
                        )
                    );
                });
            })
            .then(() => {
                console.log('[SW] App shell cached successfully');
                return self.skipWaiting();
            })
            .catch((err) => {
                console.error('[SW] Failed to cache app shell:', err);
            })
    );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => {
                            // Delete old version caches
                            return name.startsWith('weather-') &&
                                   name !== STATIC_CACHE &&
                                   name !== DYNAMIC_CACHE;
                        })
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
    );
});

/**
 * Fetch event - handle requests with appropriate caching strategy
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Determine caching strategy based on request type
    if (isApiRequest(url)) {
        // API requests: Network-first with cache fallback
        event.respondWith(networkFirstStrategy(request));
    } else if (isStaticAsset(url)) {
        // Static assets: Cache-first with network fallback
        event.respondWith(cacheFirstStrategy(request));
    } else {
        // HTML pages: Network-first for fresh content
        event.respondWith(networkFirstStrategy(request));
    }
});

/**
 * Check if request is an API call
 */
function isApiRequest(url) {
    return url.pathname.startsWith('/api/') ||
           url.pathname === '/forecast';
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(url) {
    return url.pathname.startsWith('/static/') ||
           url.hostname === 'cdn.jsdelivr.net';
}

/**
 * Cache-first strategy: Try cache, fallback to network
 */
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Not in cache, fetch from network
        const networkResponse = await fetch(request);

        // Cache the response for future use
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache-first strategy failed:', error);
        return new Response('Offline - Resource not available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

/**
 * Network-first strategy: Try network, fallback to cache
 */
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);

        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);

        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Return offline fallback for HTML requests
        if (request.headers.get('accept')?.includes('text/html')) {
            return createOfflineResponse();
        }

        // Return error for API requests
        return new Response(JSON.stringify({
            error: 'Offline',
            message: 'You appear to be offline. Please check your connection.'
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Create an offline fallback response for HTML pages
 */
function createOfflineResponse() {
    const offlineHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App - Offline</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .offline-container {
            padding: 2rem;
            max-width: 400px;
        }
        .offline-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        h1 { margin: 0 0 1rem; }
        p { opacity: 0.9; line-height: 1.6; }
        button {
            margin-top: 1.5rem;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            border: 2px solid white;
            background: transparent;
            color: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover {
            background: white;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">&#9729;</div>
        <h1>You're Offline</h1>
        <p>Weather data requires an internet connection. Please check your connection and try again.</p>
        <button onclick="location.reload()">Try Again</button>
    </div>
</body>
</html>`;

    return new Response(offlineHtml, {
        status: 200,
        headers: { 'Content-Type': 'text/html' }
    });
}

/**
 * Handle background sync for weather updates
 */
self.addEventListener('sync', (event) => {
    if (event.tag === 'weather-sync') {
        console.log('[SW] Background sync triggered');
        // Could implement background weather refresh here
    }
});

/**
 * Handle push notifications for weather alerts
 */
self.addEventListener('push', (event) => {
    if (!event.data) return;

    try {
        const data = event.data.json();

        const options = {
            body: data.body || 'Weather alert in your area',
            icon: '/static/icons/icon-192.svg',
            badge: '/static/icons/icon-192.svg',
            tag: 'weather-alert',
            requireInteraction: true,
            data: {
                url: data.url || '/'
            }
        };

        event.waitUntil(
            self.registration.showNotification(
                data.title || 'Weather Alert',
                options
            )
        );
    } catch (error) {
        console.error('[SW] Push notification error:', error);
    }
});

/**
 * Handle notification clicks
 */
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    const rawUrl = event.notification.data?.url || '/';
    // Normalize to an absolute URL so comparison with client.url works reliably
    const targetUrl = new URL(rawUrl, self.location.origin).href;

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Focus existing window if available
                for (const client of clientList) {
                    if (client.url === targetUrl && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(targetUrl);
                }
            })
    );
});
