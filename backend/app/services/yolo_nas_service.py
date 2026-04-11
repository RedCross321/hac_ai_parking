import os
import sys
import torch

try:
    from omegaconf import ListConfig, DictConfig, OmegaConf, Container
    from omegaconf.base import ContainerMetadata, Metadata

    torch.serialization.add_safe_globals([
        ListConfig, DictConfig, OmegaConf, Container,
        ContainerMetadata, Metadata,
        list, dict, tuple, set, str, int, float, bool, type(None)
    ])
    print("[✓] OmegaConf types added to torch safe globals", file=sys.stderr)
except ImportError as e:
    print(f"[⚠] OmegaConf not available: {e}", file=sys.stderr)

if not hasattr(torch.load, '_sg_legacy_patched'):
    _original_torch_load = torch.load


    def _patched_torch_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _original_torch_load(*args, **kwargs)


    _patched_torch_load._sg_legacy_patched = True
    torch.load = _patched_torch_load
    print("[✓] torch.load patched for legacy checkpoint compatibility", file=sys.stderr)

import logging
from typing import List, Dict, Optional, Any
import warnings
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
from super_gradients.training import models

logger = logging.getLogger(__name__)


class YoloNasService:
    def __init__(self, config: dict):
        self.config = config

        device_setting = config.get('device', 'auto')
        if device_setting == 'auto':
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device_setting)

        self.model = None
        self.confidence_threshold = config.get('confidence_threshold', 0.35)
        logger.info(f"YoloNasService initialized on device: {self.device}")

    def load_model(self) -> None:
        checkpoint_path = self.config['checkpoint_path']

        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Чекпоинт не найден: {checkpoint_path}")

        logger.info(f"[→] Загрузка модели '{self.config['model_name']}' из {checkpoint_path}...")

        pretrained_setting = self.config.get('pretrained_weights')
        if pretrained_setting in [None, 'None', 'none', '']:
            pretrained_weights = None
        else:
            pretrained_weights = pretrained_setting

        self.model = models.get(
            model_name=self.config['model_name'],
            num_classes=self.config['num_classes'],
            pretrained_weights=pretrained_weights,
            checkpoint_path=checkpoint_path
        )

        self.model = self.model.to(self.device).eval()
        logger.info(f"[✓] Модель загружена и перенесена на {self.device}")

    def predict_image(self, image_path: str, confidence_threshold: float = 0.35) -> Dict[str, Any]:
        """
        Выполняет предсказание на одном изображении.
        """
        if self.model is None:
            raise RuntimeError("Модель не загружена. Вызовите load_model()")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Изображение не найдено: {image_path}")

        predictions = self.model.predict(
            image_path,
            conf=confidence_threshold,
            fuse_model=self.config.get('fuse_model', True)
        )

        detections = predictions.prediction
        result = {
            "free_count": 0,
            "not_free_count": 0,
            "partially_free_count": 0,
            "total_count": 0,
        }

        classes = self.config.get('classes', [
            'free_parking_space',
            'not_free_parking_space',
            'partially_free_parking_space'
        ])

        if hasattr(detections, 'bboxes_xyxy') and detections.bboxes_xyxy is not None and len(
                detections.bboxes_xyxy) > 0:
            bboxes = detections.bboxes_xyxy
            labels = detections.labels if hasattr(detections, 'labels') else detections.class_ids
            scores = detections.confidence if hasattr(detections, 'confidence') else detections.scores

            for i in range(len(bboxes)):
                class_id = int(labels[i])
                cls_name = classes[class_id] if class_id < len(classes) else f"class_{class_id}"

                result["total_count"] += 1
                if cls_name == "free_parking_space":
                    result["free_count"] += 1
                elif cls_name == "not_free_parking_space":
                    result["not_free_count"] += 1
                elif cls_name == "partially_free_parking_space":
                    result["partially_free_count"] += 1

        return result

    def predict_images_batch(self, image_paths: List[str], confidence_threshold: float = 0.35) -> List[Dict[str, Any]]:
        """
        Выполняет предсказание на списке изображений.
        """
        results = []
        for path in image_paths:
            try:
                result = self.predict_image(path, confidence_threshold)
                result["image_path"] = path
                results.append(result)
            except Exception as e:
                results.append({
                    "image_path": path,
                    "error": str(e)
                })
        return results

_yolo_service: Optional[YoloNasService] = None

def get_yolo_service() -> YoloNasService:
    """
    Получает или создает экземпляр YoloNasService.
    """
    global _yolo_service
    if _yolo_service is None:
        from ..core.config import settings
        config = {
            'model_name': settings.YOLO_MODEL_NAME,
            'num_classes': settings.YOLO_NUM_CLASSES,
            'checkpoint_path': settings.YOLO_CHECKPOINT_PATH,
            'pretrained_weights': settings.YOLO_PRETRAINED_WEIGHTS,
            'confidence_threshold': settings.YOLO_CONFIDENCE_THRESHOLD,
            'device': settings.YOLO_DEVICE,
            'fuse_model': settings.YOLO_FUSE_MODEL,
            'classes': settings.YOLO_CLASSES
        }
        _yolo_service = YoloNasService(config)
        _yolo_service.load_model()
    return _yolo_service
