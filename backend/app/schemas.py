from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional


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
