# Интеграция с video-sever.ru - Руководство

## Обзор изменений

Данный документ описывает внесенные изменения для интеграции легальных бесплатных видеопотоков с video-sever.ru в систему мониторинга парковочных мест.

## Внесенные изменения

### 1. Конфигурация (`backend/app/core/config.py`)

Добавлены новые настройки:

```python
# Список доступных камер video-sever.ru
VIDEO_SERVER_CAMERAS: List[str] = [
    "https://srt.video-sever.ru:850/player/?key=sps861193Dqw&cam=Zaharova-12-1_cam-5",
    "https://srt.video-sever.ru:850/player/?key=sps861193Dqw&cam=Zaharova-12-1_cam-6",
    "https://srt.video-sever.ru:850/player/?key=sps861193Dqw&cam=Zaharova-12-1_cam-7",
]

# Интервал обновления скриншотов в секундах (по умолчанию 60 секунд)
SCREENSHOT_UPDATE_INTERVAL: int = 60
```

**Как добавить свои камеры:**
Отредактируйте список `VIDEO_SERVER_CAMERAS` в файле конфигурации или через переменные окружения.

### 2. Модель данных (`backend/app/models.py`)

Добавлено поле `stream_url` в модель `TestCamera`:

```python
stream_url = Column(String(1000), nullable=True)  # URL видеопотока
```

Это позволяет хранить URL видеопотока для каждой камеры.

### 3. Схема данных (`backend/app/schemas.py`)

Обновлена схема `CameraBase`:

```python
stream_url: Optional[str] = None
```

### 4. Сервис работы с потоками (`backend/app/services/camera_stream_service.py`)

Создан новый сервис для:
- Захвата скриншотов из видеопотоков
- Автоматического выполнения инференса YOLO модели
- Фоновой задачи периодического обновления (каждую минуту)

**Ключевые методы:**
- `capture_screenshot()` - захват изображения из потока
- `process_camera_stream()` - обработка потока камеры (скриншот + инференс)
- `update_all_cameras()` - обновление всех камер
- `scheduled_camera_update()` - фоновая задача (запускается каждые 60 сек)

### 5. API эндпоинты (`backend/app/routers/user.py`)

Добавлен новый эндпоинт:

```
GET /api/cameras/available
```

**Возвращает:** Список всех доступных камер с их URL видеопотоков.

При первом запросе автоматически инициализирует камеры из конфигурации.

### 6. Фоновые задачи (`backend/app/main.py`)

Добавлена фоновая задача `camera_update_task`, которая:
- Запускается при старте приложения (с задержкой 5 секунд)
- Каждую минуту обновляет скриншоты со всех камер
- Выполняет инференс модели для подсчета парковочных мест

### 7. Зависимости (`backend/requirements.txt`)

Добавлена новая зависимость:
```
aiohttp>=3.9.0
```

## Как это работает

### Архитектура

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Background Task (every 60s)          │  │
│  │                                              │  │
│  │  1. Get all cameras with stream_url          │  │
│  │  2. For each camera:                         │  │
│  │     a. Capture screenshot                    │  │
│  │     b. Save to uploads/                      │  │
│  │     c. Run YOLO inference                    │  │
│  │     d. Update TestSnapshot in DB             │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │              User API Endpoints              │  │
│  │                                              │  │
│  │  GET  /cameras/available                     │  │
│  │       → Returns list of cameras with URLs    │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   video-sever.ru       │
        │   Camera Streams       │
        └────────────────────────┘
```

### Поток данных

1. **При старте приложения:**
   - Загружается конфигурация с URL камер
   - Запускается фоновая задача обновления

2. **Каждую минуту (SCREENSHOT_UPDATE_INTERVAL):**
   - Для каждой камеры с `stream_url`:
     - Делается HTTP запрос к потоку
     - Скриншот сохраняется в `uploads/`
     - Запускается YOLO модель для детекции
     - Результаты сохраняются в БД (free_count, not_free_count, etc.)

3. **Пользовательский запрос:**
   - `GET /cameras/available` → получает список камер
   - `GET /parking/search` → получает агрегированную статистику

## Использование

### 1. Добавление камер

**Вариант A: Через конфигурацию**

Отредактируйте `backend/app/core/config.py`:

```python
VIDEO_SERVER_CAMERAS: List[str] = [
    "https://srt.video-sever.ru:850/player/?key=YOUR_KEY&cam=CAMERA_NAME_1",
    "https://srt.video-sever.ru:850/player/?key=YOUR_KEY&cam=CAMERA_NAME_2",
    # Добавьте нужные камеры
]
```

**Вариант B: Через API**

```bash
POST /test/cameras
Content-Type: application/json

{
    "name": "My Camera",
    "location": "Street Name 123",
    "latitude": 55.751244,
    "longitude": 37.618423,
    "stream_url": "https://srt.video-sever.ru:850/player/?key=..."
}
```

### 2. Получение списка камер

```bash
curl http://localhost:8000/api/cameras/available
```

**Ответ:**
```json
[
    {
        "id": 1,
        "name": "Zaharova-12-1_cam-5",
        "location": "video-sever.ru - Камера 1",
        "latitude": null,
        "longitude": null,
        "stream_url": "https://srt.video-sever.ru:850/player/?key=sps861193Dqw&cam=Zaharova-12-1_cam-5",
        "status": "ok",
        "created_at": "2025-01-15T10:00:00",
        "updated_at": "2025-01-15T10:01:00"
    }
]
```

### 3. Поиск парковок

```bash
curl "http://localhost:8000/api/parking/search?lat=55.751244&lon=37.618423&radius=1000"
```

**Ответ:**
```json
{
    "total_free": 15,
    "total_not_free": 42,
    "total_partially_free": 3,
    "total_count": 60,
    "cameras_count": 3,
    "snapshot_path": "uploads/camera_1_20250115_100100.png",
    "message": "Найдено 3 камер в радиусе 1000м"
}
```

## Настройка интервала обновления

Для изменения частоты обновления скриншотов:

**В config.py:**
```python
SCREENSHOT_UPDATE_INTERVAL: int = 120  # Обновление каждые 2 минуты
```

**Или через .env:**
```
SCREENSHOT_UPDATE_INTERVAL=120
```

## Обработка ошибок

Сервис автоматически обрабатывает ошибки:

- **Недоступный поток:** Создается placeholder изображение
- **Ошибка инференса:** Статус камеры устанавливается в "inference_error"
- **Таймаут:** Повторная попытка при следующем цикле

## Мониторинг

Статусы камер:
- `pending` - Камера добавлена, ожидает первого обновления
- `ok` - Камера работает нормально
- `error` - Ошибка при захвате скриншота
- `inference_error` - Ошибка при выполнении инференса модели
- `camera_unreachable` - Поток недоступен

## Требования к системе

- Python 3.8+
- aiohttp>=3.9.0
- PIL/Pillow (для создания placeholder изображений)
- YOLO модель (уже установлена в проекте)

## Производительность

Рекомендации:
- Для большого количества камер увеличьте `SCREENSHOT_UPDATE_INTERVAL`
- Используйте асинхронные запросы (уже реализовано)
- Рассмотрите возможность кэширования результатов инференса

## Безопасность

- URL камер хранятся в конфигурации
- Доступ к API требует аутентификации (для некоторых эндпоинтов)
- CORS настроен для localhost:5173 (frontend)

## Отладка

Логи выводятся в консоль:
```
[INFO] Обновление камеры 1: Zaharova-12-1_cam-5
[INFO] Инференс завершен: 15 свободных, 42 занятых
[WARNING] Ошибка при захвате скриншота: Timeout
```

## Будущие улучшения

Возможные доработки:
1. Поддержка RTSP потоков (через OpenCV/ffmpeg)
2. Кэширование скриншотов в Redis
3. Вебхуки для уведомления об изменениях
4. Приоритизация камер при обновлении
5. Адаптивный интервал обновления на основе активности

## Контакты и поддержка

Для добавления новых камер или вопросов обращайтесь к документации video-sever.ru.
