import os
import random
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import TestCamera, TestSnapshot, UserRequest
from ..schemas import (
    GeoResolveRequest,
    GeoResolveResponse,
    ParkingSearchResponse,
    TripSessionCreate,
    TripSessionResponse,
    TripSessionCancelResponse,
    NotificationResponse,
    NotificationsPullResponse,
)
from ..dependencies import get_current_user
from ..models import User
from .. import crud

router = APIRouter(tags=["user-api"])


@router.post("/geo/resolve", response_model=GeoResolveResponse)
async def resolve_geo_address(
    request: GeoResolveRequest,
    db: Session = Depends(get_db)
):
    """
    Геокодирование адреса - получение координат по адресу.
    
    В тестовом режиме возвращает фиктивные координаты для любого адреса.
    
    - **address**: Адрес для геокодирования
    
    Возвращает координаты и нормализованный адрес.
    """
    # Stub implementation - returns mock coordinates based on address hash
    # In production, this would call a geocoding service (Google Maps, Yandex, OSM)
    
    # Generate deterministic mock coordinates based on address
    addr_hash = hash(request.address)
    latitude = 55.751244 + (addr_hash % 1000) / 10000  # Moscow region offset
    longitude = 37.618423 + (addr_hash % 500) / 10000
    
    # Log the request
    db.add(UserRequest(
        endpoint="/geo/resolve",
        method="POST",
        request_data=request.address,
        response_status=200
    ))
    db.commit()
    
    return GeoResolveResponse(
        latitude=latitude,
        longitude=longitude,
        address=request.address
    )


@router.get("/parking/search", response_model=ParkingSearchResponse)
async def search_parking(
    lat: Optional[float] = Query(None, description="Широта"),
    lon: Optional[float] = Query(None, description="Долгота"),
    address: Optional[str] = Query(None, description="Адрес (альтернатива координатам)"),
    radius: int = Query(1000, description="Радиус поиска в метрах (по умолчанию 1000м)"),
    db: Session = Depends(get_db)
):
    """
    Поиск доступных парковочных мест в радиусе от адреса или координат.
    
    - **lat**: Широта (если не указан address)
    - **lon**: Долгота (если не указан address)
    - **address**: Адрес для поиска (альтернатива координатам)
    - **radius**: Радиус поиска в метрах (максимум 1000м)
    
    Возвращает агрегированную статистику свободных мест в радиусе.
    """
    # Validate input
    if address is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать либо address, либо пару lat/lon"
        )
    
    # Limit radius to 1000m as per requirements
    radius = min(radius, 1000)
    
    # If address is provided, we would normally geocode it first
    # For now, use provided coordinates or mock coordinates from address
    if address and (lat is None or lon is None):
        # Mock geocoding - in production call /geo/resolve or external service
        addr_hash = hash(address)
        lat = 55.751244 + (addr_hash % 1000) / 10000
        lon = 37.618423 + (addr_hash % 500) / 10000
    
    # Get all cameras (in MVP we don't filter by distance yet since we have test data)
    # In production, this would filter by actual distance using Haversine formula
    cameras = db.query(TestCamera).all()
    
    if not cameras:
        # No cameras available - return stub with test snapshot
        test_snapshot_path = _get_test_snapshot_path()
        
        # Log the request
        db.add(UserRequest(
            endpoint="/parking/search",
            method="GET",
            request_data=f"lat={lat}, lon={lon}, address={address}, radius={radius}",
            response_status=200
        ))
        db.commit()
        
        return ParkingSearchResponse(
            total_free=0,
            total_not_free=0,
            total_partially_free=0,
            total_count=0,
            cameras_count=0,
            snapshot_path=test_snapshot_path,
            message="Камеры не найдены в указанном радиусе. Возвращаем тестовое изображение."
        )
    
    # Get latest snapshots for each camera
    latest_snapshots = []
    for camera in cameras:
        latest_snapshot = db.query(TestSnapshot).filter(
            TestSnapshot.camera_id == camera.id
        ).order_by(TestSnapshot.created_at.desc()).first()
        
        if latest_snapshot:
            latest_snapshots.append(latest_snapshot)
    
    # Aggregate statistics from all snapshots
    total_free = sum(s.free_count for s in latest_snapshots)
    total_not_free = sum(s.not_free_count for s in latest_snapshots)
    total_partially_free = sum(s.partially_free_count for s in latest_snapshots)
    total_count = sum(s.total_count for s in latest_snapshots)
    
    # Get a test snapshot path for display (stub - in production would show actual camera feed)
    test_snapshot_path = _get_test_snapshot_path()
    
    # Log the request
    db.add(UserRequest(
        endpoint="/parking/search",
        method="GET",
        request_data=f"lat={lat}, lon={lon}, address={address}, radius={radius}",
        response_status=200
    ))
    db.commit()
    
    return ParkingSearchResponse(
        total_free=total_free,
        total_not_free=total_not_free,
        total_partially_free=total_partially_free,
        total_count=total_count,
        cameras_count=len(cameras),
        snapshot_path=test_snapshot_path,
        message=f"Найдено {len(cameras)} камер в радиусе {radius}м"
    )


def _get_test_snapshot_path() -> str:
    """
    Получить путь к тестовому снимку из папки testSnapshots.
    Возвращает случайный снимок для демонстрации.
    """
    test_snapshots_dir = os.path.join(os.path.dirname(__file__), "../../testSnapshots")
    
    if os.path.exists(test_snapshots_dir):
        images = [f for f in os.listdir(test_snapshots_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        
        if images:
            # Return relative path that can be served statically
            selected_image = random.choice(images)
            return f"testSnapshots/{selected_image}"
    
    return None


# Trip Monitoring Endpoints

@router.post("/trip-monitoring/sessions", response_model=TripSessionResponse)
async def create_trip_session(
    request: TripSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую сессию поездки для текущего пользователя.
    
    - **start_latitude**: Начальная широта (опционально)
    - **start_longitude**: Начальная долгота (опционально)
    
    Возвращает созданную сессию поездки со статусом "active".
    """
    trip_session = crud.create_trip_session(
        db=db,
        user_id=current_user.id,
        start_latitude=request.start_latitude,
        start_longitude=request.start_longitude
    )
    
    # Log the request
    db.add(UserRequest(
        endpoint="/trip-monitoring/sessions",
        method="POST",
        request_data=f"start_lat={request.start_latitude}, start_lon={request.start_longitude}",
        response_status=200
    ))
    db.commit()
    
    return trip_session


@router.get("/trip-monitoring/sessions/{trip_session_id}", response_model=TripSessionResponse)
async def get_trip_session(
    trip_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о сессии поездки по ID.
    
    - **trip_session_id**: ID сессии поездки
    
    Возвращает данные сессии поездки, если она принадлежит текущему пользователю.
    """
    trip_session = crud.get_trip_session(db=db, trip_session_id=trip_session_id)
    
    if not trip_session:
        raise HTTPException(status_code=404, detail="Сессия поездки не найдена")
    
    # Проверка прав доступа - сессия должна принадлежать текущему пользователю
    if trip_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Log the request
    db.add(UserRequest(
        endpoint=f"/trip-monitoring/sessions/{trip_session_id}",
        method="GET",
        request_data="",
        response_status=200
    ))
    db.commit()
    
    return trip_session


@router.post("/trip-monitoring/sessions/{trip_session_id}/cancel", response_model=TripSessionCancelResponse)
async def cancel_trip_session(
    trip_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отменить активную сессию поездки.
    
    - **trip_session_id**: ID сессии поездки для отмены
    
    Отменяет только активные сессии. Если сессия уже завершена или отменена,
    возвращается ошибка.
    """
    trip_session = crud.get_trip_session(db=db, trip_session_id=trip_session_id)
    
    if not trip_session:
        raise HTTPException(status_code=404, detail="Сессия поездки не найдена")
    
    # Проверка прав доступа
    if trip_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Отмена сессии
    cancelled_session = crud.cancel_trip_session(db=db, trip_session_id=trip_session_id)
    
    if not cancelled_session:
        raise HTTPException(status_code=400, detail="Не удалось отменить сессию. Возможно, она уже завершена")
    
    # Создание уведомления об отмене
    crud.create_notification(
        db=db,
        user_id=current_user.id,
        title="Поездка отменена",
        message=f"Сессия поездки #{trip_session_id} была отменена",
        trip_session_id=trip_session_id,
        notification_type="info"
    )
    
    # Log the request
    db.add(UserRequest(
        endpoint=f"/trip-monitoring/sessions/{trip_session_id}/cancel",
        method="POST",
        request_data="",
        response_status=200
    ))
    db.commit()
    
    return TripSessionCancelResponse(
        trip_session_id=cancelled_session.id,
        status=cancelled_session.status,
        message="Сессия поездки успешно отменена",
        cancelled_at=cancelled_session.cancelled_at
    )


@router.get("/trip-monitoring/notifications/pull", response_model=NotificationsPullResponse)
async def get_notifications_pull(
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество уведомлений"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список непрочитанных уведомлений для текущего пользователя.
    
    - **limit**: Максимальное количество уведомлений (1-100, по умолчанию 50)
    
    Возвращает только непрочитанные уведомления, отсортированные по дате создания
    (новые первыми). После получения уведомления не помечаются как прочитанные.
    """
    notifications = crud.get_unread_notifications(db=db, user_id=current_user.id, limit=limit)
    
    # Log the request
    db.add(UserRequest(
        endpoint="/trip-monitoring/notifications/pull",
        method="GET",
        request_data=f"limit={limit}",
        response_status=200
    ))
    db.commit()
    
    return NotificationsPullResponse(
        notifications=notifications,
        count=len(notifications)
    )


@router.post("/trip-monitoring/notifications/read", response_model=dict)
async def mark_notifications_as_read(
    notification_id: Optional[int] = Query(None, description="ID конкретного уведомления (если не указано, отмечаются все)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отметить уведомления как прочитанные.
    
    - **notification_id**: ID конкретного уведомления (опционально).
      Если не указан, отмечаются все непрочитанные уведомления пользователя.
    
    Возвращает количество отмеченных уведомлений.
    """
    if notification_id is not None:
        # Отметить конкретное уведомление
        notification = crud.mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        if not notification:
            raise HTTPException(status_code=404, detail="Уведомление не найдено")
        
        count = 1
    else:
        # Отметить все уведомления
        count = crud.mark_all_notifications_as_read(db=db, user_id=current_user.id)
    
    # Log the request
    db.add(UserRequest(
        endpoint="/trip-monitoring/notifications/read",
        method="POST",
        request_data=f"notification_id={notification_id}",
        response_status=200
    ))
    db.commit()
    
    return {
        "marked_count": count,
        "message": f"Отмечено {count} уведомлений как прочитанные"
    }
