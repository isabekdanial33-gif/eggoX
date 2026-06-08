// EggoX Service Worker
// Стратегия: Cache First для статики, Network First для Firebase
const SW_VERSION = 'eggox-v1.0';
const STATIC_CACHE = SW_VERSION + '-static';
const DYNAMIC_CACHE = SW_VERSION + '-dynamic';

// Файлы для кэширования при установке (app shell)
const PRECACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  // Шрифты Google подгрузятся автоматически при первом запуске
];

// Домены которые НЕ кэшируем (Firebase, API, стримы)
const NO_CACHE_DOMAINS = [
  'firebaseio.com',
  'firebase.googleapis.com',
  'firestore.googleapis.com',
  'googleapis.com',
  'metered.ca',
  'metered.live',
  'fonts.googleapis.com',   // заголовки запрещают кэш
];

// ── Установка: кэшируем app shell ───────────────────────────────
self.addEventListener('install', event => {
  console.log('[SW] Installing', SW_VERSION);
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll(PRECACHE).catch(err => {
        console.warn('[SW] Pre-cache partial failure:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// ── Активация: удаляем старые кэши ──────────────────────────────
self.addEventListener('activate', event => {
  console.log('[SW] Activating', SW_VERSION);
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== STATIC_CACHE && k !== DYNAMIC_CACHE)
          .map(k => { console.log('[SW] Deleting old cache:', k); return caches.delete(k); })
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: стратегия по типу запроса ────────────────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 1. Не кэшируем Firebase, API, медиа-стримы
  if (NO_CACHE_DOMAINS.some(d => url.hostname.includes(d))) {
    return; // браузер делает сам
  }

  // 2. Не кэшируем не-GET запросы
  if (event.request.method !== 'GET') return;

  // 3. Не кэшируем chrome-extension и другие схемы
  if (!url.protocol.startsWith('http')) return;

  // 4. HTML навигация — Network First (всегда свежий index.html)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(STATIC_CACHE).then(c => c.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // 5. Статические ресурсы (иконки, шрифты, cdnjs) — Cache First
  const isStatic =
    url.pathname.match(/\.(png|jpg|jpeg|gif|webp|svg|ico|woff2?|ttf)$/) ||
    url.hostname.includes('cdnjs.cloudflare.com') ||
    url.hostname.includes('fonts.gstatic.com');

  if (isStatic) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(DYNAMIC_CACHE).then(c => c.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // 6. Всё остальное — Network First с fallback на кэш
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then(c => c.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// ── Push уведомления (FCM) ───────────────────────────────────────
self.addEventListener('push', event => {
  let data = {};
  try { data = event.data.json(); } catch(e) { data = { title: 'EggoX', body: event.data?.text() || 'Новое сообщение' }; }

  const title = data.title || 'EggoX';
  const options = {
    body:    data.body || 'Новое сообщение',
    icon:    '/icons/icon-192.png',
    badge:   '/icons/icon-96.png',
    vibrate: [100, 50, 100],
    data:    { url: data.url || '/' },
    actions: [
      { action: 'open',    title: 'Открыть' },
      { action: 'dismiss', title: 'Закрыть' }
    ]
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// ── Клик по уведомлению ──────────────────────────────────────────
self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'dismiss') return;
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      const existing = list.find(c => c.url.includes(self.location.origin));
      if (existing) { existing.focus(); existing.postMessage({ type: 'NOTIFICATION_CLICK', url }); }
      else clients.openWindow(url);
    })
  );
});

// ── Сообщения от страницы ────────────────────────────────────────
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});
