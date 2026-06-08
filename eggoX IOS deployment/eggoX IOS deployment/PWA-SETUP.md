# 🥚 EggoX — Иконки PWA

## Как получить все иконки

1. Открой файл `generate-icons.html` в браузере (Chrome/Safari)
2. Нажми кнопку **«Скачать все иконки»**
3. Скачаются PNG-файлы: `icon-57.png`, `icon-60.png`, ..., `icon-512.png`
4. Создай папку `icons/` рядом с `index.html`
5. Положи все скачанные файлы в `icons/`

## Структура папки проекта

```
📁 твой-сайт/
  ├── index.html
  ├── manifest.json
  ├── service-worker.js
  ├── generate-icons.html   (только для генерации, в продакшен не нужен)
  └── 📁 icons/
        ├── icon-57.png
        ├── icon-60.png
        ├── icon-72.png
        ├── icon-76.png
        ├── icon-96.png
        ├── icon-114.png
        ├── icon-120.png
        ├── icon-144.png
        ├── icon-152.png
        ├── icon-180.png
        ├── icon-192.png
        └── icon-512.png
```

## Splash screens (опционально)

Если хочешь splash screen при запуске на iPhone — создай PNG нужных размеров
и положи в `icons/`:
- `splash-390x844.png` — iPhone 12/13/14
- `splash-428x926.png` — iPhone 12/13/14 Pro Max
- `splash-375x812.png` — iPhone X/XS/11 Pro
- `splash-414x896.png` — iPhone XR/11
- `splash-375x667.png` — iPhone 6/7/8

Рекомендуемый размер: 2× от указанного (retina).
Фон: `#f1fbf4`, логотип по центру.

## Как добавить на экран Домой (iPhone)

1. Открой сайт в **Safari**
2. Нажми **Поделиться** (квадрат со стрелкой вверх)
3. Выбери **«На экран Домой»**
4. Нажми **Добавить**

Приложение запустится в полноэкранном режиме без адресной строки Safari.

## Push-уведомления

Service Worker уже поддерживает Push. Для полноценных push-уведомлений
когда приложение закрыто — нужно подключить **Firebase Cloud Messaging (FCM)**:
1. Firebase Console → Cloud Messaging → Web Push certificates
2. Получи VAPID key
3. Добавь в код регистрацию FCM токена
