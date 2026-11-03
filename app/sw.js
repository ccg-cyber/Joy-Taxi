self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('push', function (e) {
  var d = {}; try { d = e.data.json(); } catch (_) {}
  e.waitUntil(self.registration.showNotification(d.title || 'New ride request', { body: d.body || '', icon: '/app/icon-192.png', badge: '/app/icon-192.png', tag: 'ride', renotify: true, vibrate: [200, 100, 200], data: { url: d.url || '/app/driver/' } }));
});
self.addEventListener('notificationclick', function (e) {
  e.notification.close(); var u = (e.notification.data && e.notification.data.url) || '/app/driver/';
  e.waitUntil(self.clients.matchAll({ type: 'window' }).then(function (l) { for (var c of l) if (c.url.indexOf('/app/') > -1 && 'focus' in c) return c.focus(); return self.clients.openWindow(u); }));
});
