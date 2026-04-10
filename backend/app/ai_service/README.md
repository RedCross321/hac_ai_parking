# AI Service for Parking Detection

## Обзор

Модуль AI для анализа изображений с камер наблюдения и определения:
1. **Количества свободных парковочных мест**
2. **Класса автомобилей (A/B/C/D/PICKUP)** на занятых местах

Модуль разработан в соответствии с техническим заданием из `README.md v1.2`.

## Структура модуля

```
ai_service/
├── __init__.py              # Инициализация модуля
├── config.py                # Конфигурация и модели данных
├── README_AI.md             # Полная документация
├── models/
│   ├── __init__.py
│   ├── parking_detector.py    # Детекция парковочных мест
│   └── vehicle_classifier.py  # Классификация автомобилей
├── preprocess/
│   ├── __init__.py
│   └── image_processor.py     # Предобработка изображений
├── inference/
│   ├── __init__.py
│   └── predictor.py           # Основной пайплайн предсказания
└── utils/
    ├── __init__.py
    └── visualization.py       # Визуализация результатов
```

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Базовое использование

```python
from app.ai_service.inference import ParkingPredictor
from app.ai_service.config import AIConfig
import numpy as np

# Создание конфигурации
config = AIConfig(
    confidence_threshold=0.5,
    device="cpu"
)

# Инициализация предиктора
predictor = ParkingPredictor(config)
predictor.initialize()

# Загрузка изображения
image = np.load("path/to/image.npy")  # или используйте bytes, path

# Предсказание
result = predictor.predict(
    image_source=image,
    camera_id="camera_001"
)

# Результаты
print(f"Свободных мест: {result.free_spaces}/{result.total_spaces}")
print(f"Занятых мест: {result.occupied_spaces}")
print(f"Распределение по классам: {result.vehicle_classes}")
print(f"Время обработки: {result.processing_time_ms}мс")
```

### 3. Использование с байтами изображения

```python
# Из файла
with open("parking.jpg", "rb") as f:
    image_bytes = f.read()

result = predictor.predict(
    image_source=image_bytes,
    camera_id="camera_001"
)
```

### 4. Конфигурация раскладки парковки для камеры

```python
# Определение парковочных мест для конкретной камеры
spaces = [
    {
        'space_id': 'space_1',
        'bbox': (100, 100, 200, 250),  # (x1, y1, x2, y2)
    },
    {
        'space_id': 'space_2',
        'bbox': (210, 100, 310, 250),
    },
    # ... больше мест
]

predictor.configure_camera_layout("camera_001", spaces)
```

## Классы автомобилей

Согласно README.md v1.2 section 1.2:

| Класс | Описание | Примеры |
|-------|----------|---------|
| **A** | Micro/mini cars | Smart Fortwo, Fiat 500 |
| **B** | Small cars | VW Polo, Ford Fiesta |
| **C** | Medium cars | VW Golf, Toyota Corolla |
| **D** | Large cars | BMW 5 Series, Mercedes E-Class |
| **PICKUP** | Pickup trucks | Ford F-150, Toyota Hilux |

## API контракты

### Входные данные

```python
{
    "image_source": Union[bytes, str, np.ndarray],
    "camera_id": str,
    "timestamp": Optional[str]  # ISO format
}
```

### Выходные данные (DetectionResult)

```python
{
    "camera_id": str,
    "timestamp": str,
    "total_spaces": int,
    "free_spaces": int,
    "occupied_spaces": int,
    "vehicle_classes": {
        "A": int,
        "B": int,
        "C": int,
        "D": int,
        "PICKUP": int
    },
    "overall_confidence": float,
    "processing_time_ms": int,
    "success": bool,
    "error_message": Optional[str]
}
```

## Архитектурные фазы

### MVP (текущая реализация)
- ✅ Эвристическая детекция на основе контраста/текстуры
- ✅ Базовая классификация по размеру
- ✅ Интеграция с preprocessing pipeline
- ✅ Конфигурируемые параметры

### Pilot Production (следующий этап)
- [ ] YOLOv8/v10 для детекции автомобилей
- [ ] Custom classifier для точной классификации
- [ ] Сегментация парковочных мест
- [ ] Обучение на размеченных данных

### Scale
- [ ] Вынос в отдельный микросервис
- [ ] Очереди задач (RabbitMQ/Kafka)
- [ ] Кэширование результатов
- [ ] GPU acceleration

## Конфигурация

### Параметры AIConfig

```python
config = AIConfig(
    # Модель
    model_name="yolov8n",
    
    # Производительность
    max_processing_time_ms=2000,  # p95 target
    confidence_threshold=0.5,
    iou_threshold=0.45,
    
    # Обработка изображений
    input_image_size=640,
    enable_augmentation=False,
    
    # Устройство
    device="cpu",  # cpu/cuda/mps
    batch_size=1,
    
    # Кэширование
    enable_caching=True,
    cache_ttl_seconds=60,
    
    # Fallback
    fallback_to_heuristics=True,
    min_confidence_for_result=0.3
)
```

### Переменные окружения

```bash
AI_MODEL_NAME=yolov8n
AI_CONFIDENCE_THRESHOLD=0.5
AI_DEVICE=cpu
AI_MAX_PROCESSING_TIME_MS=2000
```

## Тестирование

### Запуск тестов

```bash
cd backend
python -c "
from app.ai_service.inference import ParkingPredictor
from app.ai_service.config import AIConfig
import numpy as np

config = AIConfig()
predictor = ParkingPredictor(config)
predictor.initialize()

test_image = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
result = predictor.predict(test_image, camera_id='test_cam')

print(f'Test passed: {result.success}')
print(f'Processing time: {result.processing_time_ms}ms < 2000ms target')
"
```

## Интеграция с Backend

### Интеграция с ingestion API

```python
# В вашем FastAPI endpoint для /test/screenshots
from app.ai_service.inference import ParkingPredictor
from app.ai_service.config import AIConfig

predictor = ParkingPredictor(AIConfig())
predictor.initialize()

@app.post("/test/screenshots")
async def upload_screenshot(
    camera_id: str,
    file: UploadFile
):
    image_bytes = await file.read()
    result = predictor.predict(image_bytes, camera_id)
    
    # Сохранение результата в БД
    # ...
    
    return {
        "free_spaces": result.free_spaces,
        "total_spaces": result.total_spaces,
        "vehicle_classes": result.model_dump_json_safe()["vehicle_classes"]
    }
```

## Мониторинг и метрики

### Технические метрики
- Время обработки одного изображения (цель: p95 < 2000мс)
- Процент успешных обработок
- Использование CPU/GPU

### Бизнес-метрики
- Точность определения свободных мест
- Точность классификации автомобилей
- Confidence score модели

## Правовые аспекты

Согласно разделу 9 (Риски) README.md:
- ✅ Использовать только whitelist источников камер
- ✅ Legal review по каждому источнику
- ✅ Не показывать первичные кадры в клиенте
- ✅ Соблюдать законодательство РФ о персональных данных

## Расширение функциональности

### Добавление поддержки ML моделей

1. Раскомментируйте зависимости в `requirements.txt`:
```
ultralytics==8.1.0
torch==2.1.0
torchvision==0.16.0
```

2. Обновите `models/parking_detector.py` и `models/vehicle_classifier.py` для загрузки YOLO

3. Обучите модель на размеченных данных парковок

### Добавление новой классификации

1. Добавьте новый класс в `VehicleClass` enum в `config.py`
2. Обновите `VEHICLE_CLASS_DIMENSIONS` в `vehicle_classifier.py`
3. Обновите цветовую схему в `utils/visualization.py`

## Лицензия

Часть проекта hac_ai_parking. См. LICENSE файл.
