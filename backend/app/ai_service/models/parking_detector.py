"""
Parking Space Detector

Detects parking spaces in images and determines their occupancy status.
Implements both heuristic (MVP) and ML-based (Pilot+) approaches.
"""

import logging
from typing import Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class ParkingDetector:
    """
    Parking space detection and occupancy analysis
    
    According to README.md v1.2:
    - MVP: Heuristic/manual input via free_* fields
    - Pilot+: CV/ML pipeline for auto and parking space detection
    """
    
    def __init__(self, config=None):
        """
        Initialize parking detector
        
        Args:
            config: AIConfig instance with model parameters
        """
        self.config = config
        self.model = None
        self.is_initialized = False
        
        # Predefined parking space templates (for MVP/pilot)
        # In production, these would be learned or configured per camera
        self.parking_space_templates = {}
        
    def load_model(self, model_path: Optional[str] = None):
        """
        Load parking detection model
        
        Args:
            model_path: Path to trained model weights
            
        For MVP: Initializes heuristic-based detector
        For Pilot+: Loads ML model (YOLO-Seg, Mask R-CNN, etc.)
        """
        try:
            if model_path:
                # TODO: Load trained ML model for production
                logger.info(f"Loading ML model from {model_path}")
                # Implementation for Pilot+ stage:
                # from ultralytics import YOLO
                # self.model = YOLO(model_path)
                self.is_initialized = True
            else:
                # MVP: Use heuristic approach
                logger.info("Initializing heuristic parking detector (MVP mode)")
                self.is_initialized = True
                
        except Exception as e:
            logger.error(f"Failed to load parking detector model: {e}")
            if self.config and self.config.fallback_to_heuristics:
                logger.warning("Falling back to heuristics")
                self.is_initialized = True
            else:
                raise
    
    def detect_spaces(self, image: np.ndarray) -> List[dict]:
        """
        Detect parking spaces in image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected parking spaces with bbox and metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Model not initialized. Call load_model() first.")
        
        # MVP: Return predefined template or simple heuristic
        # This should be replaced with actual ML inference in Pilot+
        logger.debug("Running parking space detection (heuristic mode)")
        
        # Placeholder implementation
        # In production: run ML model inference
        parking_spaces = self._heuristic_detection(image)
        
        return parking_spaces
    
    def analyze_occupancy(
        self, 
        image: np.ndarray, 
        parking_spaces: List[dict],
        vehicle_detections: Optional[List[dict]] = None
    ) -> List[dict]:
        """
        Analyze occupancy status of detected parking spaces
        
        Args:
            image: Input image
            parking_spaces: List of detected parking spaces
            vehicle_detections: Optional vehicle detections from VehicleClassifier
            
        Returns:
            List of parking spaces with occupancy status
        """
        if not parking_spaces:
            return []
        
        # If vehicle detections provided, use them to determine occupancy
        if vehicle_detections:
            return self._match_vehicles_to_spaces(
                parking_spaces, 
                vehicle_detections
            )
        else:
            # Fallback: analyze spaces directly
            return self._analyze_spaces_directly(image, parking_spaces)
    
    def _heuristic_detection(self, image: np.ndarray) -> List[dict]:
        """
        Heuristic parking space detection for MVP
        
        Uses simple image processing to identify potential parking spaces
        """
        height, width = image.shape[:2]
        
        # MVP placeholder: return grid of hypothetical spaces
        # In real implementation, this would use:
        # 1. Pre-configured space locations per camera
        # 2. Perspective transformation to bird's eye view
        # 3. Line detection to find parking markings
        
        num_spaces_x = max(1, width // 100)  # Assume ~100px per space
        num_spaces_y = max(1, height // 150)  # Assume ~150px per space
        
        spaces = []
        space_id = 0
        
        for y in range(num_spaces_y):
            for x in range(num_spaces_x):
                x1 = x * 100
                y1 = y * 150
                x2 = min((x + 1) * 100, width)
                y2 = min((y + 1) * 150, height)
                
                spaces.append({
                    'space_id': f'space_{space_id}',
                    'bbox': (x1, y1, x2, y2),
                    'area': (x2 - x1) * (y2 - y1),
                    'confidence': 0.5  # Low confidence for heuristic
                })
                space_id += 1
        
        return spaces
    
    def _match_vehicles_to_spaces(
        self, 
        parking_spaces: List[dict],
        vehicle_detections: List[dict]
    ) -> List[dict]:
        """
        Match detected vehicles to parking spaces using IoU
        """
        result = []
        
        for space in parking_spaces:
            space_bbox = space['bbox']
            is_occupied = False
            matched_vehicle = None
            max_iou = 0
            
            for vehicle in vehicle_detections:
                vehicle_bbox = vehicle.get('bbox')
                if not vehicle_bbox:
                    continue
                    
                iou = self._calculate_iou(space_bbox, vehicle_bbox)
                
                if iou > max_iou and iou > 0.3:  # IoU threshold
                    max_iou = iou
                    is_occupied = True
                    matched_vehicle = vehicle
            
            space_result = {
                **space,
                'is_occupied': is_occupied,
                'vehicle_class': matched_vehicle.get('class') if matched_vehicle else None,
                'confidence': max_iou if is_occupied else space.get('confidence', 0.5)
            }
            
            if is_occupied and matched_vehicle:
                space_result['vehicle_confidence'] = matched_vehicle.get('confidence', 0.0)
            
            result.append(space_result)
        
        return result
    
    def _analyze_spaces_directly(
        self, 
        image: np.ndarray, 
        parking_spaces: List[dict]
    ) -> List[dict]:
        """
        Analyze space occupancy directly from image (fallback method)
        
        Uses color/texture analysis to detect presence of vehicles
        """
        result = []
        
        for space in parking_spaces:
            x1, y1, x2, y2 = space['bbox']
            space_roi = image[y1:y2, x1:x2]
            
            # Simple heuristic: analyze color variance
            # Vehicles typically have different colors than asphalt
            if space_roi.size > 0:
                variance = np.var(space_roi)
                # Higher variance might indicate presence of vehicle
                is_occupied = variance > 1000  # Threshold needs tuning
            else:
                is_occupied = False
            
            result.append({
                **space,
                'is_occupied': is_occupied,
                'vehicle_class': None,
                'confidence': 0.4  # Low confidence for heuristic
            })
        
        return result
    
    def _calculate_iou(self, bbox1: tuple, bbox2: tuple) -> float:
        """Calculate Intersection over Union between two bboxes"""
        x1, y1, x2, y2 = bbox1
        x3, y3, x4, y4 = bbox2
        
        # Calculate intersection
        xi1 = max(x1, x3)
        yi1 = max(y1, y3)
        xi2 = min(x2, x4)
        yi2 = min(y2, y4)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        # Calculate union
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x4 - x3) * (y4 - y3)
        union_area = box1_area + box2_area - inter_area
        
        # Calculate IoU
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou
    
    def configure_camera_layout(self, camera_id: str, spaces: List[dict]):
        """
        Configure predefined parking space layout for a specific camera
        
        Args:
            camera_id: Camera identifier
            spaces: List of parking space definitions with bboxes
        """
        self.parking_space_templates[camera_id] = spaces
        logger.info(f"Configured {len(spaces)} parking spaces for camera {camera_id}")
    
    def get_camera_layout(self, camera_id: str) -> Optional[List[dict]]:
        """Get predefined parking space layout for a camera"""
        return self.parking_space_templates.get(camera_id)
