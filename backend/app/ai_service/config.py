"""
Configuration for AI Service

Defines configuration parameters and vehicle classes according to README.md v1.2
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class VehicleClass(str, Enum):
    """Vehicle classification according to README.md v1.2 section 1.2"""
    A = "A"           # Micro/mini cars
    B = "B"           # Small cars
    C = "C"           # Medium cars
    D = "D"           # Large cars
    PICKUP = "PICKUP" # Pickup trucks


class AIConfig(BaseModel):
    """
    Configuration for AI parking detection service
    
    According to README.md v1.2 non-functional requirements:
    - Performance: p95 <= 2 seconds
    - Reliability: partial data availability support
    - Freshness: up to 1 update per minute
    """
    
    # Model configuration
    model_name: str = Field(
        default="yolov8n",
        description="Base model for vehicle detection (yolov8n/yolov8s/yolov8m)"
    )
    vehicle_classifier_model: Optional[str] = Field(
        default=None,
        description="Path to fine-tuned vehicle classifier model"
    )
    parking_detector_model: Optional[str] = Field(
        default=None,
        description="Path to parking space detection model"
    )
    
    # Performance settings
    max_processing_time_ms: int = Field(
        default=2000,
        description="Maximum processing time per image (p95 target from README)"
    )
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for detections"
    )
    iou_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="IoU threshold for NMS"
    )
    
    # Image processing
    input_image_size: int = Field(
        default=640,
        description="Input image size for model"
    )
    enable_augmentation: bool = Field(
        default=False,
        description="Enable test-time augmentation for better accuracy"
    )
    
    # Device configuration
    device: str = Field(
        default="cpu",
        description="Device for inference (cpu/cuda/mps)"
    )
    batch_size: int = Field(
        default=1,
        description="Batch size for inference"
    )
    
    # Caching
    enable_caching: bool = Field(
        default=True,
        description="Enable result caching for identical images"
    )
    cache_ttl_seconds: int = Field(
        default=60,
        description="Cache TTL in seconds (matches 1 update/min requirement)"
    )
    
    # Fallback behavior
    fallback_to_heuristics: bool = Field(
        default=True,
        description="Fallback to simple heuristics if ML model fails"
    )
    min_confidence_for_result: float = Field(
        default=0.3,
        description="Minimum confidence to return result instead of fallback"
    )
    
    class Config:
        env_prefix = "AI_"
        case_sensitive = False


class ParkingSpaceStatus(BaseModel):
    """Represents status of a single parking space"""
    space_id: str
    is_occupied: bool
    vehicle_class: Optional[VehicleClass] = None
    confidence: float
    bbox: Optional[tuple] = None  # (x1, y1, x2, y2)


class DetectionResult(BaseModel):
    """
    Result of parking lot analysis
    
    Output format for integration with backend aggregation
    """
    camera_id: str
    timestamp: str
    
    # Space counts
    total_spaces: int
    free_spaces: int
    occupied_spaces: int
    
    # Vehicle distribution by class
    vehicle_classes: dict[VehicleClass, int] = Field(
        default_factory=lambda: {vc: 0 for vc in VehicleClass}
    )
    
    # Quality metrics
    overall_confidence: float
    processing_time_ms: int
    
    # Detailed information
    spaces: list[ParkingSpaceStatus] = Field(default_factory=list)
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    
    def model_dump_json_safe(self) -> dict:
        """Convert to JSON-serializable dict"""
        data = self.model_dump()
        # Convert VehicleClass enum keys to strings
        if 'vehicle_classes' in data:
            data['vehicle_classes'] = {
                key.value if hasattr(key, 'value') else key: value
                for key, value in data['vehicle_classes'].items()
            }
        return data
