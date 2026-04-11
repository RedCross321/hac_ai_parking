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
)

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
