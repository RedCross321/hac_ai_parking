from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# === Camera Schemas ===
class CameraBase(BaseModel):
    name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Snapshot Schemas ===
class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: DetectionBox


class InferenceResult(BaseModel):
    free_count: int
    not_free_count: int
    partially_free_count: int
    total_count: int
    detections: Optional[List[DetectionResult]] = Field(default=None, exclude=True)

    # detections: List[DetectionResult]


class SnapshotUploadResponse(BaseModel):
    snapshot_id: int
    camera_id: int
    image_path: str
    inference_result: Optional[InferenceResult] = None
    status: str
    message: str


class BatchUploadResponse(BaseModel):
    total_uploaded: int
    successful: int
    failed: int
    results: List[SnapshotUploadResponse]


# === Health Check ===
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str