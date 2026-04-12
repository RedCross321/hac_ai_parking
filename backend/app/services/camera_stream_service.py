import asyncio
import aiohttp
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import base64
import io

# Исправляем импорты для корректной работы внутри пакета services
try:
    from app.database import get_db
    from app.models import TestCamera, TestSnapshot
    from app.core.config import settings
except ImportError:
    from ..database import get_db
    from ..models import TestCamera, TestSnapshot
    from ..core.config import settings


def get_yolo_service():
    """Lazy import yolo service to avoid circular dependencies."""
    try:
        from app.services.yolo_nas_service import get_yolo_service as _get_service
        return _get_service()
    except ImportError:
        from .yolo_nas_service import get_yolo_service as _get_service
        return _get_service()


class CameraStreamService:
    """Сервис для работы с видеопотоками камер."""
    
    def __init__(self):
        self.screenshot_dirs: dict[int, str] = {}
    
    async def capture_screenshot(self, stream_url: str, timeout: int = 30) -> Optional[bytes]:
        """
        Сделать скриншот из видеопотока.
        
        Args:
            stream_url: URL видеопотока
            timeout: Таймаут запроса в секундах
            
        Returns:
            Байты изображения или None при ошибке
        """
        # video-sever.ru предоставляет поток через HTML5 player
        # Для получения скриншота нужно использовать HTTP запрос к потоку
        # или использовать ffmpeg/opencv для захвата
        
        try:
            # Попытка получить скриншот через HTTP запрос
            # Некоторые серверы предоставляют отдельный endpoint для скриншотов
            screenshot_url = stream_url.replace("/player/?", "/snapshot/?")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(screenshot_url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.read()
                    
            # Если snapshot endpoint не работает, пробуем оригинальный URL
            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url, timeout=timeout) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        
                        # Если это изображение, возвращаем его
                        if 'image/' in content_type:
                            return await response.read()
                        
                        # Если это HTML страница с плеером, нужно использовать другой подход
                        # В этом случае возвращаем None и используем заглушку
                        return None
                        
        except Exception as e:
            print(f"Ошибка при захвате скриншота: {e}")
            return None
    
    def generate_placeholder_screenshot(self, camera_name: str) -> bytes:
        """
        Создать placeholder изображение для камеры.
        
        Args:
            camera_name: Название камеры
            
        Returns:
            Байты PNG изображения
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем изображение 640x480
        img = Image.new('RGB', (640, 480), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)
        
        # Добавляем текст с названием камеры
        text = f"Camera: {camera_name}"
        # Используем шрифт по умолчанию
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Вычисляем позицию текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (640 - text_width) // 2
        y = (480 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        draw.text((x, y + 40), "Stream unavailable", fill=(200, 200, 200), font=font)
        
        # Сохраняем в bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.read()
    
    async def process_camera_stream(
        self, 
        db: Session, 
        camera: TestCamera,
        run_inference: bool = True
    ) -> Optional[TestSnapshot]:
        """
        Обработать видеопоток камеры: сделать скриншот и выполнить инференс.
        
        Args:
            db: Сессия базы данных
            camera: Объект камеры
            run_inference: Выполнять ли инференс модели
            
        Returns:
            Объект снимка или None при ошибке
        """
        # Захват скриншота
        screenshot_bytes = await self.capture_screenshot(camera.stream_url)
        
        if screenshot_bytes is None:
            # Если не удалось получить скриншот, создаем placeholder
            screenshot_bytes = self.generate_placeholder_screenshot(camera.name)
        
        # Сохранение скриншота
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        filename = f"camera_{camera.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(screenshot_bytes)
        
        # Создание записи снимка в БД
        db_snapshot = TestSnapshot(
            camera_id=camera.id,
            image_path=file_path,
            inference_status="processing" if run_inference else "completed"
        )
        db.add(db_snapshot)
        db.commit()
        db.refresh(db_snapshot)
        
        # Инференс модели
        if run_inference:
            try:
                yolo_service = get_yolo_service()
                result = yolo_service.predict_image(
                    file_path,
                    confidence_threshold=settings.YOLO_CONFIDENCE_THRESHOLD
                )
                
                # Обновление записи снимка
                db_snapshot.free_count = result["free_count"]
                db_snapshot.not_free_count = result["not_free_count"]
                db_snapshot.partially_free_count = result["partially_free_count"]
                db_snapshot.total_count = result["total_count"]
                db_snapshot.inference_status = "completed"
                
                # Обновление статуса камеры
                camera.status = "ok"
                camera.updated_at = datetime.utcnow()
                
            except Exception as e:
                db_snapshot.inference_status = "failed"
                db_snapshot.error_message = str(e)
                camera.status = "inference_error"
                print(f"Ошибка инференса: {e}")
        
        db.commit()
        return db_snapshot
    
    async def update_all_cameras(self, db: Session):
        """
        Обновить все камеры: сделать скриншоты и выполнить инференс.
        
        Args:
            db: Сессия базы данных
        """
        cameras = db.query(TestCamera).filter(
            TestCamera.stream_url.isnot(None)
        ).all()
        
        for camera in cameras:
            try:
                await self.process_camera_stream(db, camera)
            except Exception as e:
                print(f"Ошибка обработки камеры {camera.id}: {e}")
                camera.status = "error"
                db.commit()


# Глобальный экземпляр сервиса
camera_stream_service = CameraStreamService()


async def scheduled_camera_update():
    """
    Фоновая задача для периодического обновления скриншотов камер.
    Запускается каждые SCREENSHOT_UPDATE_INTERVAL секунд.
    """
    while True:
        try:
            # Получаем сессию БД
            db = next(get_db())
            
            # Обновляем все камеры
            await camera_stream_service.update_all_cameras(db)
            
            db.close()
            
        except Exception as e:
            print(f"Ошибка в фоновой задаче обновления камер: {e}")
        
        # Ждем следующий интервал
        await asyncio.sleep(settings.SCREENSHOT_UPDATE_INTERVAL)
