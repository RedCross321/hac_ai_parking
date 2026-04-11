from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Общие настройки
    APP_NAME: str = "PEasy"
    DEBUG: bool = True

    # База данных
    DATABASE_URL: str = "sqlite:///./test_mode.db"

    # Настройки YOLO-NAS
    YOLO_MODEL_NAME: str = "yolo_nas_l"
    YOLO_NUM_CLASSES: int = 3
    YOLO_CHECKPOINT_PATH: str = "models/average_model.pth"
    YOLO_PRETRAINED_WEIGHTS: Optional[str] = None
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35
    YOLO_DEVICE: str = "auto"  # auto, cuda, cpu
    YOLO_FUSE_MODEL: bool = True
    YOLO_CLASSES: List[str] = [
        "free_parking_space",
        "not_free_parking_space",
        "partially_free_parking_space"
    ]

    # Настройки загрузки файлов
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()