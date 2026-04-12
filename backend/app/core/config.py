from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Настройки приложения."""
    APP_NAME: str = "PEasy"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./test_mode.db"

    YOLO_MODEL_NAME: str = "yolo_nas_l"
    YOLO_NUM_CLASSES: int = 3
    YOLO_CHECKPOINT_PATH: str = "models/average_model.pth"
    YOLO_PRETRAINED_WEIGHTS: Optional[str] = None
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35
    YOLO_DEVICE: str = "auto"
    YOLO_FUSE_MODEL: bool = True
    YOLO_CLASSES: List[str] = [
        "free_parking_space",
        "not_free_parking_space",
        "partially_free_parking_space"
    ]

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]

    YANDEX_SMARTCAPTCHA_SERVER_KEY: str 
    YANDEX_SMARTCAPTCHA_SITE_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()