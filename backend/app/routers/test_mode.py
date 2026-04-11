import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import TestCamera, TestSnapshot, UserRequest
from ..schemas import (
    CameraResponse,
    CameraCreate,
    SnapshotUploadResponse,
    BatchUploadResponse,
    InferenceResult,
    DetectionResult,
    DetectionBox
)
from ..services.yolo_nas_service import get_yolo_service, YoloNasService
from ..core.config import settings

router = APIRouter(prefix="/test", tags=["test-mode"])

def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

@router.get("/cameras", response_model=List[CameraResponse])
async def get_cameras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех камер в тестовом режиме.

    Возвращает информацию о камерах, включая их статус и количество снимков.
    """
    cameras = db.query(TestCamera).order_by(desc(TestCamera.created_at)).offset(skip).limit(limit).all()
    return cameras


@router.post("/cameras", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    """
    Добавить новую камеру в тестовый режим.
    """
    db_camera = TestCamera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.post("/screenshots", response_model=SnapshotUploadResponse)
async def upload_screenshot(
    file: UploadFile = File(..., description="Изображение с камеры"),
    camera_id: Optional[int] = Form(None, description="ID камеры (если есть)"),
    camera_name: Optional[str] = Form(None, description="Название камеры (если camera_id не указан)"),
    run_inference: bool = Form(True, description="Запустить ли инференс модели"),
    db: Session = Depends(get_db),
    yolo_service: YoloNasService = Depends(get_yolo_service)
):
    """
    Загрузить скриншот с камеры и выполнить детекцию парковочных мест.

    - **file**: Изображение в формате JPG, PNG, BMP, TIFF
    - **camera_id**: ID существующей камеры (опционально)
    - **camera_name**: Название новой камеры (если camera_id не указан)
    - **run_inference**: Запустить ли модель детекции (по умолчанию True)

    Возвращает результат анализа изображения с количеством свободных мест.
    """
    # Проверка расширения файла
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    if ext.lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат файла. Разрешены: {settings.ALLOWED_EXTENSIONS}"
        )

    # Определение или создание камеры
    if camera_id:
        db_camera = db.query(TestCamera).filter(TestCamera.id == camera_id).first()
        if not db_camera:
            raise HTTPException(status_code=404, detail=f"Камера с ID {camera_id} не найдена")
    else:
        camera_name = camera_name or f"Camera-{uuid.uuid4().hex[:8]}"
        db_camera = TestCamera(name=camera_name, status="ok")
        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)

    # Создание записи снимка
    db_snapshot = TestSnapshot(
        camera_id=db_camera.id,
        image_path="../../testSnapshots",
        inference_status="processing" if run_inference else "completed"
    )
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)

    file_path = save_uploaded_file(file, settings.UPLOAD_DIR)

    # Инференс модели
    inference_result = None
    if run_inference:
        try:
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

            # Преобразование в схему
            inference_result = InferenceResult(
                free_count=result["free_count"],
                not_free_count=result["not_free_count"],
                partially_free_count=result["partially_free_count"],
                total_count=result["total_count"],
                detections=None  # ✅ Явно указываем None
            )


            # Обновление статуса камеры
            db_camera.status = "ok"
            db_camera.updated_at = datetime.utcnow()

        except Exception as e:
            db_snapshot.inference_status = "failed"
            db_snapshot.error_message = str(e)
            db_camera.status = "camera_unreachable"
            raise HTTPException(status_code=500, detail=f"Ошибка инференса: {str(e)}")

    db.commit()

    # Логирование запроса
    db.add(UserRequest(
        endpoint="/test/screenshots",
        method="POST",
        response_status=200
    ))
    db.commit()

    return SnapshotUploadResponse(
        snapshot_id=db_snapshot.id,
        camera_id=db_camera.id,
        image_path=file_path,
        inference_result=inference_result,
        status="success",
        message=f"Обработано {inference_result.total_count if inference_result else 0} объектов"
    )


@router.post("/batch-screenshots", response_model=BatchUploadResponse)
async def upload_batch_screenshots(
    files: List[UploadFile] = File(..., description="Список изображений"),
    camera_ids: Optional[str] = Form(None, description="CSV список ID камер"),
    run_inference: bool = Form(True, description="Запустить ли инференс модели"),
    db: Session = Depends(get_db),
    yolo_service: YoloNasService = Depends(get_yolo_service)
):
    """
    Загрузить несколько скриншотов одновременно для пакетной обработки.

    - **files**: Список изображений
    - **camera_ids**: CSV список ID камер (опционально, если не указан - создаются новые камеры)
    - **run_inference**: Запустить ли модель детекции

    Возвращает агрегированный результат обработки всех изображений.
    """
    results = []
    successful = 0
    failed = 0

    # Парсинг camera_ids если указан
    camera_id_list = None
    if camera_ids:
        try:
            camera_id_list = [int(x.strip()) for x in camera_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="camera_ids должен быть CSV списком целых чисел")

    for idx, file in enumerate(files):
        try:
            # Проверка расширения
            ext = os.path.splitext(file.filename)[1] if file.filename else ""
            if ext.lower() not in settings.ALLOWED_EXTENSIONS:
                failed += 1
                results.append(SnapshotUploadResponse(
                    snapshot_id=0,
                    camera_id=0,
                    image_path="",
                    status="failed",
                    message=f"Недопустимый формат: {ext}"
                ))
                continue

            # Сохранение файла
            file_path = save_uploaded_file(file, settings.UPLOAD_DIR)

            # Определение камеры
            camera_id = camera_id_list[idx] if camera_id_list and idx < len(camera_id_list) else None

            if camera_id:
                db_camera = db.query(TestCamera).filter(TestCamera.id == camera_id).first()
                if not db_camera:
                    failed += 1
                    results.append(SnapshotUploadResponse(
                        snapshot_id=0,
                        camera_id=camera_id,
                        image_path=file_path,
                        status="failed",
                        message=f"Камера {camera_id} не найдена"
                    ))
                    continue
            else:
                camera_name = f"Batch-Camera-{uuid.uuid4().hex[:8]}"
                db_camera = TestCamera(name=camera_name, status="ok")
                db.add(db_camera)
                db.commit()
                db.refresh(db_camera)

            # Создание записи снимка
            db_snapshot = TestSnapshot(
                camera_id=db_camera.id,
                image_path=file_path,
                inference_status="processing" if run_inference else "completed"
            )
            db.add(db_snapshot)
            db.commit()
            db.refresh(db_snapshot)

            # Инференс
            inference_result = None
            if run_inference:
                result = yolo_service.predict_image(
                    file_path,
                    confidence_threshold=settings.YOLO_CONFIDENCE_THRESHOLD
                )

                db_snapshot.free_count = result["free_count"]
                db_snapshot.not_free_count = result["not_free_count"]
                db_snapshot.partially_free_count = result["partially_free_count"]
                db_snapshot.total_count = result["total_count"]
                db_snapshot.inference_status = "completed"

                inference_result = InferenceResult(
                    free_count=result["free_count"],
                    not_free_count=result["not_free_count"],
                    partially_free_count=result["partially_free_count"],
                    total_count=result["total_count"],
                    detections=None  # ✅ Без детекций
                )

                db_camera.status = "ok"
                db_camera.updated_at = datetime.utcnow()

            db.commit()

            successful += 1
            results.append(SnapshotUploadResponse(
                snapshot_id=db_snapshot.id,
                camera_id=db_camera.id,
                image_path=file_path,
                inference_result=inference_result,
                status="success",
                message=f"Обработано {inference_result.total_count if inference_result else 0} объектов"
            ))

        except Exception as e:
            failed += 1
            results.append(SnapshotUploadResponse(
                snapshot_id=0,
                camera_id=0,
                image_path="",
                status="failed",
                message=str(e)
            ))

    # Логирование
    db.add(UserRequest(
        endpoint="/test/batch-screenshots",
        method="POST",
        response_status=200
    ))
    db.commit()

    return BatchUploadResponse(
        total_uploaded=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


@router.get("/health")
async def health_check(yolo_service: YoloNasService = Depends(get_yolo_service)):
    """
    Проверка здоровья сервиса и статуса загрузки модели.
    """
    return {
        "status": "healthy" if yolo_service.model is not None else "unhealthy",
        "model_loaded": yolo_service.model is not None,
        "device": str(yolo_service.device)
    }