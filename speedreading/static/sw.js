const CACHE_NAME    = 'speedreader-v1';
const OFFLINE_URL   = '/offline/';

// files to cache immediately on install
const PRECACHE_URLS = [
    '/',
    '/login/',
    '/dashboard/',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lora:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@400;600&display=swap',
];

// ── INSTALL ──────────────────────────────────────────
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(PRECACHE_URLS);
        }).then(function() {
            return self.skipWaiting();
        })
    );
});

// ── ACTIVATE ─────────────────────────────────────────
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames
                    .filter(function(name) { return name !== CACHE_NAME; })
                    .map(function(name) { return caches.delete(name); })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

// ── FETCH ─────────────────────────────────────────────
self.addEventListener('fetch', function(event) {
    // skip non-GET and API calls
    if (event.request.method !== 'GET') return;
    if (event.request.url.includes('/admin/')) return;
    if (event.request.url.includes('/learn/assistant/ask/')) return;
    if (event.request.url.includes('/custom/')) return;

    event.respondWith(
        fetch(event.request)
            .then(function(response) {
                // cache successful responses
                if (response && response.status === 200) {
                    var responseClone = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(function() {
                // offline fallback — serve from cache
                return caches.match(event.request).then(function(cached) {
                    if (cached) return cached;
                    // if page not in cache → show offline page
                    if (event.request.destination === 'document') {
                        return caches.match(OFFLINE_URL);
                    }
                });
            })
    );
});