from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

class BootstrapAdminRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class BootstrapAdminResponse(BaseModel):
    message: str
    admin_email: str

class TokenResponse(BaseModel):
    bootstrap_token: str
    message: str

class ErrorResponse(BaseModel):
    detail: str

class UserCreate(BaseModel):
    """Схема для создания пользователя."""
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    """Схема вывода данных пользователя."""
    id: int
    username: str
    email: str


class CameraBase(BaseModel):
    """Базовая схема камеры."""
    name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CameraCreate(CameraBase):
    """Схема для создания камеры."""
    pass


class CameraResponse(CameraBase):
    """Схема ответа с данными камеры."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема JWT токена."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема данных токена."""
    username: str | None = None


class ForgotPasswordRequest(BaseModel):
    """Схема запроса на восстановление пароля."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Схема запроса на сброс пароля."""
    token: str
    new_password: str


class DetectionBox(BaseModel):
    """Схема bounding box детекции."""
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionResult(BaseModel):
    """Схема результата детекции."""
    class_id: int
    class_name: str
    confidence: float
    bbox: DetectionBox


class InferenceResult(BaseModel):
    """Схема результата инференса модели."""
    free_count: int
    not_free_count: int
    partially_free_count: int
    total_count: int
    detections: Optional[List[DetectionResult]] = Field(default=None, exclude=True)


class SnapshotUploadResponse(BaseModel):
    """Схема ответа при загрузке снимка."""
    snapshot_id: int
    camera_id: int
    image_path: str
    inference_result: Optional[InferenceResult] = None
    status: str
    message: str


class BatchUploadResponse(BaseModel):
    """Схема ответа при пакетной загрузке."""
    total_uploaded: int
    successful: int
    failed: int
    results: List[SnapshotUploadResponse]


class HealthResponse(BaseModel):
    """Схема ответа health check."""
    status: str
    model_loaded: bool
    device: str


class GeoResolveRequest(BaseModel):
    """Схема запроса для геокодирования адреса."""
    address: str


class GeoResolveResponse(BaseModel):
    """Схема ответа для геокодирования."""
    latitude: float
    longitude: float
    address: str


class ParkingSearchResponse(BaseModel):
    """Схема ответа для поиска парковки."""
    total_free: int
    total_not_free: int
    total_partially_free: int
    total_count: int
    cameras_count: int
    snapshot_path: Optional[str] = None
    message: str


# Trip Monitoring Schemas

class TripSessionCreate(BaseModel):
    """Схема для создания сессии поездки."""
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None


class TripSessionResponse(BaseModel):
    """Схема ответа с данными сессии поездки."""
    id: int
    user_id: int
    status: str
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TripSessionCancelResponse(BaseModel):
    """Схема ответа при отмене сессии поездки."""
    trip_session_id: int
    status: str
    message: str
    cancelled_at: datetime


class NotificationResponse(BaseModel):
    """Схема ответа с данными уведомления."""
    id: int
    user_id: int
    trip_session_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    notification_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationsPullResponse(BaseModel):
    """Схема ответа для pull уведомлений."""
    notifications: List[NotificationResponse]
    count: int
