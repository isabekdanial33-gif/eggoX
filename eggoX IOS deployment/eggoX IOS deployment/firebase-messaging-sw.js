// firebase-messaging-sw.js
// Place this file at the ROOT of your website (same folder as index.html).
// FCM requires it to be at exactly this path.

importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js');

// Must match the config in index.html exactly
firebase.initializeApp({
  apiKey: "AIzaSyD7aJ5jb3ZpLVOl2DWXzUcIaDrPuuKEBXo",
  authDomain: "dancela-messenger.firebaseapp.com",
  databaseURL: "https://dancela-messenger-default-rtdb.firebaseio.com",
  projectId: "dancela-messenger",
  storageBucket: "dancela-messenger.firebasestorage.app",
  messagingSenderId: "376383770466",
  appId: "1:376383770466:web:6a7e3e7814d327c25b663b"
});

const messaging = firebase.messaging();

// Handle background push messages (app is closed or in background)
messaging.onBackgroundMessage(payload => {
  const { title = 'EggoX', body = 'Новое сообщение', icon = '/icons/icon-192.png' } = payload.notification || {};
  self.registration.showNotification(title, {
    body,
    icon,
    badge: '/icons/icon-72.png',
    tag: payload.collapseKey || 'eggox-msg',
    data: payload.data || {},
    renotify: true,
  });
});

// Tap on a background notification → open / focus the app
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      const app = list.find(c => c.url.includes(self.location.origin) && 'focus' in c);
      if (app) return app.focus();
      return clients.openWindow('/');
    })
  );
});
