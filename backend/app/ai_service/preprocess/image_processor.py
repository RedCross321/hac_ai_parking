"""
Image Preprocessing Module

Handles image loading, normalization, and augmentation for the AI pipeline.
"""

import logging
from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image preprocessing for parking detection pipeline
    
    Handles:
    - Loading images from various sources (bytes, files, URLs)
    - Resizing and normalization
    - Color space conversion
    - Data augmentation (optional)
    """
    
    def __init__(self, config=None):
        """
        Initialize image processor
        
        Args:
            config: AIConfig instance with processing parameters
        """
        self.config = config
        self.default_size = config.input_image_size if config else 640
        
    def load_image(
        self, 
        source: Union[bytes, str, np.ndarray],
        source_type: Optional[str] = None
    ) -> np.ndarray:
        """
        Load image from various sources
        
        Args:
            source: Image data (bytes, file path, or numpy array)
            source_type: Type of source ('bytes', 'path', 'array', 'auto')
            
        Returns:
            Image as numpy array in RGB format
        """
        if source_type == 'auto' or source_type is None:
            source_type = self._detect_source_type(source)
        
        try:
            if source_type == 'bytes':
                return self._load_from_bytes(source)
            elif source_type == 'path':
                return self._load_from_path(source)
            elif source_type == 'array':
                return self._validate_array(source)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
                
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise
    
    def _detect_source_type(self, source: Union[bytes, str, np.ndarray]) -> str:
        """Automatically detect source type"""
        if isinstance(source, bytes):
            return 'bytes'
        elif isinstance(source, str):
            return 'path'
        elif isinstance(source, np.ndarray):
            return 'array'
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")
    
    def _load_from_bytes(self, data: bytes) -> np.ndarray:
        """Load image from bytes"""
        image = Image.open(io.BytesIO(data))
        return self._pil_to_numpy(image)
    
    def _load_from_path(self, path: str) -> np.ndarray:
        """Load image from file path"""
        image = Image.open(path)
        return self._pil_to_numpy(image)
    
    def _validate_array(self, array: np.ndarray) -> np.ndarray:
        """Validate and convert numpy array to standard format"""
        if array.ndim not in [2, 3]:
            raise ValueError(f"Invalid array dimensions: {array.ndim}")
        
        # Convert grayscale to RGB
        if array.ndim == 2:
            array = np.stack([array] * 3, axis=-1)
        
        # Ensure we have 3 channels
        if array.shape[-1] == 4:  # RGBA
            array = array[:, :, :3]
        elif array.shape[-1] == 1:
            array = np.stack([array.squeeze()] * 3, axis=-1)
        
        return array
    
    def _pil_to_numpy(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy array"""
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        return np.array(pil_image)
    
    def preprocess(
        self,
        image: np.ndarray,
        target_size: Optional[int] = None,
        normalize: bool = True,
        keep_aspect_ratio: bool = True
    ) -> Tuple[np.ndarray, dict]:
        """
        Preprocess image for model inference
        
        Args:
            image: Input image as numpy array
            target_size: Target size for resizing (default from config)
            normalize: Whether to normalize pixel values to [0, 1]
            keep_aspect_ratio: Whether to preserve aspect ratio
            
        Returns:
            Tuple of (preprocessed_image, metadata)
            metadata contains:
                - original_size: (height, width)
                - resized_size: (height, width)
                - scale_factor: Scaling applied
                - padding: Padding applied if keeping aspect ratio
        """
        size = target_size or self.default_size
        original_height, original_width = image.shape[:2]
        
        # Resize
        if keep_aspect_ratio:
            resized_image, scale_factor, padding = self._resize_with_padding(
                image, size
            )
        else:
            resized_image = self._resize_simple(image, size)
            scale_factor = (size / original_width, size / original_height)
            padding = (0, 0)
        
        # Normalize
        if normalize:
            resized_image = resized_image.astype(np.float32) / 255.0
        
        metadata = {
            'original_size': (original_height, original_width),
            'resized_size': resized_image.shape[:2],
            'scale_factor': scale_factor,
            'padding': padding
        }
        
        return resized_image, metadata
    
    def _resize_with_padding(
        self, 
        image: np.ndarray, 
        target_size: int
    ) -> Tuple[np.ndarray, Tuple[float, float], Tuple[int, int]]:
        """
        Resize image keeping aspect ratio with padding
        
        Returns:
            Tuple of (resized_image, scale_factor, padding)
        """
        original_height, original_width = image.shape[:2]
        
        # Calculate scale factor
        scale = min(target_size / original_width, target_size / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize
        resized = self._resize_simple(image, new_width, new_height)
        
        # Create padded canvas
        canvas = np.zeros((target_size, target_size, 3), dtype=image.dtype)
        
        # Calculate padding
        pad_top = (target_size - new_height) // 2
        pad_left = (target_size - new_width) // 2
        
        # Place resized image on canvas
        canvas[pad_top:pad_top+new_height, pad_left:pad_left+new_width] = resized
        
        scale_factor = (scale, scale)
        padding = (pad_left, pad_top)
        
        return canvas, scale_factor, padding
    
    def _resize_simple(
        self, 
        image: np.ndarray, 
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> np.ndarray:
        """Simple resize using PIL"""
        pil_image = Image.fromarray(image)
        
        if width and height:
            new_size = (width, height)
        elif width:
            scale = width / image.shape[1]
            new_height = int(image.shape[0] * scale)
            new_size = (width, new_height)
        elif height:
            scale = height / image.shape[0]
            new_width = int(image.shape[1] * scale)
            new_size = (new_width, height)
        else:
            return image
        
        resized = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        return np.array(resized)
    
    def postprocess_detections(
        self,
        detections: list,
        metadata: dict
    ) -> list:
        """
        Transform detections back to original image coordinates
        
        Args:
            detections: List of detections with bbox in preprocessed coordinates
            metadata: Metadata from preprocess step
            
        Returns:
            Detections with bboxes transformed to original image coordinates
        """
        scale_x, scale_y = metadata['scale_factor']
        pad_x, pad_y = metadata['padding']
        
        processed_detections = []
        
        for det in detections:
            bbox = det.get('bbox')
            if not bbox:
                processed_detections.append(det)
                continue
            
            x1, y1, x2, y2 = bbox
            
            # Remove padding and scale back
            orig_x1 = (x1 - pad_x) / scale_x
            orig_y1 = (y1 - pad_y) / scale_y
            orig_x2 = (x2 - pad_x) / scale_x
            orig_y2 = (y2 - pad_y) / scale_y
            
            # Clip to original image bounds
            orig_height, orig_width = metadata['original_size']
            orig_x1 = max(0, min(orig_x1, orig_width))
            orig_y1 = max(0, min(orig_y1, orig_height))
            orig_x2 = max(0, min(orig_x2, orig_width))
            orig_y2 = max(0, min(orig_y2, orig_height))
            
            processed_det = {**det, 'bbox': (orig_x1, orig_y1, orig_x2, orig_y2)}
            processed_detections.append(processed_det)
        
        return processed_detections
    
    def enhance_image(
        self,
        image: np.ndarray,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0
    ) -> np.ndarray:
        """
        Apply image enhancement
        
        Args:
            image: Input image
            brightness: Brightness multiplier (1.0 = no change)
            contrast: Contrast multiplier (1.0 = no change)
            sharpness: Sharpness multiplier (1.0 = no change)
            
        Returns:
            Enhanced image
        """
        pil_image = Image.fromarray(image)
        
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(sharpness)
        
        return np.array(pil_image)


# Import ImageEnhance if available
try:
    from PIL import ImageEnhance
except ImportError:
    ImageEnhance = None
