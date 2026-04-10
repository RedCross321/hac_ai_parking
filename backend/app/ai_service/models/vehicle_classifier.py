"""
Vehicle Classifier

Detects and classifies vehicles by class (A/B/C/D/PICKUP) in parking lot images.
Implements both heuristic (MVP) and ML-based (Pilot+) approaches.
"""

import logging
from typing import Optional, List, Dict
import numpy as np

from ..config import VehicleClass

logger = logging.getLogger(__name__)


class VehicleClassifier:
    """
    Vehicle detection and classification
    
    According to README.md v1.2 section 1.2:
    - Classifies vehicles into categories: A/B/C/D/PICKUP
    - Returns distribution of vehicle classes for occupied spaces
    
    Architecture phases:
    - MVP: Heuristic detection with basic size estimation
    - Pilot+: YOLO-based detection with custom classifier head
    """
    
    # Vehicle class definitions based on typical dimensions
    VEHICLE_CLASS_DIMENSIONS = {
        VehicleClass.A: {'length': (2.5, 3.5), 'width': (1.4, 1.7)},  # Micro/mini
        VehicleClass.B: {'length': (3.5, 4.2), 'width': (1.6, 1.8)},  # Small
        VehicleClass.C: {'length': (4.2, 4.7), 'width': (1.7, 1.9)},  # Medium
        VehicleClass.D: {'length': (4.7, 5.5), 'width': (1.8, 2.1)},  # Large
        VehicleClass.PICKUP: {'length': (5.0, 6.5), 'width': (1.8, 2.2)},  # Pickup
    }
    
    def __init__(self, config=None):
        """
        Initialize vehicle classifier
        
        Args:
            config: AIConfig instance with model parameters
        """
        self.config = config
        self.detection_model = None
        self.classification_model = None
        self.is_initialized = False
        
    def load_model(self, detection_model_path: Optional[str] = None, 
                   classifier_model_path: Optional[str] = None):
        """
        Load vehicle detection and classification models
        
        Args:
            detection_model_path: Path to vehicle detection model (YOLO, etc.)
            classifier_model_path: Path to fine-tuned classifier model
            
        For MVP: Initializes heuristic-based detector
        For Pilot+: Loads ML models
        """
        try:
            if detection_model_path:
                # TODO: Load trained ML model for production
                logger.info(f"Loading vehicle detection model from {detection_model_path}")
                # Implementation for Pilot+ stage:
                # from ultralytics import YOLO
                # self.detection_model = YOLO(detection_model_path)
                self.is_initialized = True
            else:
                # MVP: Use heuristic approach
                logger.info("Initializing heuristic vehicle classifier (MVP mode)")
                self.is_initialized = True
                
            if classifier_model_path:
                logger.info(f"Loading vehicle classifier from {classifier_model_path}")
                # TODO: Load classification model
                # self.classification_model = load_classifier(classifier_model_path)
                
        except Exception as e:
            logger.error(f"Failed to load vehicle classifier model: {e}")
            if self.config and self.config.fallback_to_heuristics:
                logger.warning("Falling back to heuristics")
                self.is_initialized = True
            else:
                raise
    
    def detect_and_classify(
        self, 
        image: np.ndarray,
        confidence_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Detect vehicles in image and classify them by class
        
        Args:
            image: Input image as numpy array (RGB or BGR)
            confidence_threshold: Override default confidence threshold
            
        Returns:
            List of detected vehicles with:
            - bbox: (x1, y1, x2, y2)
            - class: VehicleClass enum
            - confidence: Detection confidence
            - class_confidence: Classification confidence
        """
        if not self.is_initialized:
            raise RuntimeError("Model not initialized. Call load_model() first.")
        
        threshold = confidence_threshold or (
            self.config.confidence_threshold if self.config else 0.5
        )
        
        logger.debug(f"Running vehicle detection (threshold={threshold})")
        
        # MVP: Heuristic detection
        # In Pilot+: Run ML model inference
        detections = self._heuristic_detection(image, threshold)
        
        return detections
    
    def _heuristic_detection(
        self, 
        image: np.ndarray, 
        threshold: float
    ) -> List[Dict]:
        """
        Heuristic vehicle detection for MVP
        
        Uses simple blob detection and size estimation
        This is a placeholder for the ML-based approach in Pilot+
        """
        detections = []
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = np.mean(image, axis=2)
        else:
            gray = image
        
        height, width = gray.shape
        
        # Simple blob detection using variance
        # In real implementation, use proper object detection
        block_size = 50
        stride = 25
        
        for y in range(0, height - block_size, stride):
            for x in range(0, width - block_size, stride):
                roi = gray[y:y+block_size, x:x+block_size]
                
                # Calculate local contrast
                variance = np.var(roi)
                mean_intensity = np.mean(roi)
                
                # Vehicles typically have higher contrast than background
                if variance > 1500 and 50 < mean_intensity < 200:
                    # Estimate size and classify
                    estimated_length = block_size * 0.1  # Rough scale factor
                    estimated_width = block_size * 0.05
                    
                    vehicle_class = self._estimate_vehicle_class(
                        estimated_length, 
                        estimated_width
                    )
                    
                    confidence = min(1.0, variance / 5000)
                    
                    if confidence >= threshold:
                        detections.append({
                            'bbox': (x, y, x + block_size, y + block_size),
                            'class': vehicle_class,
                            'confidence': confidence,
                            'class_confidence': 0.5,  # Low confidence for heuristic
                            'area': block_size * block_size
                        })
        
        # Apply non-maximum suppression to remove overlapping detections
        detections = self._nms(detections, iou_threshold=0.5)
        
        return detections
    
    def _estimate_vehicle_class(
        self, 
        length: float, 
        width: float
    ) -> VehicleClass:
        """
        Estimate vehicle class based on estimated dimensions
        
        Args:
            length: Estimated vehicle length in meters
            width: Estimated vehicle width in meters
            
        Returns:
            VehicleClass enum value
        """
        best_class = VehicleClass.B  # Default to medium-small
        best_score = float('inf')
        
        for vehicle_class, dimensions in self.VEHICLE_CLASS_DIMENSIONS.items():
            length_range = dimensions['length']
            width_range = dimensions['width']
            
            # Calculate distance from center of range
            length_center = (length_range[0] + length_range[1]) / 2
            width_center = (width_range[0] + width_range[1]) / 2
            
            distance = ((length - length_center) ** 2 + 
                       (width - width_center) ** 2) ** 0.5
            
            if distance < best_score:
                best_score = distance
                best_class = vehicle_class
        
        return best_class
    
    def _nms(self, detections: List[Dict], iou_threshold: float) -> List[Dict]:
        """
        Apply Non-Maximum Suppression to remove overlapping detections
        
        Args:
            detections: List of detection dictionaries
            iou_threshold: IoU threshold for suppression
            
        Returns:
            Filtered list of detections
        """
        if not detections:
            return []
        
        # Sort by confidence
        detections_sorted = sorted(
            detections, 
            key=lambda x: x['confidence'], 
            reverse=True
        )
        
        keep = []
        while detections_sorted:
            best = detections_sorted.pop(0)
            keep.append(best)
            
            # Remove detections with high IoU
            detections_sorted = [
                det for det in detections_sorted
                if self._calculate_iou(best['bbox'], det['bbox']) < iou_threshold
            ]
        
        return keep
    
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
        
        return inter_area / union_area if union_area > 0 else 0
    
    def count_by_class(self, detections: List[Dict]) -> Dict[VehicleClass, int]:
        """
        Count detected vehicles by class
        
        Args:
            detections: List of vehicle detections
            
        Returns:
            Dictionary mapping VehicleClass to count
        """
        counts = {vc: 0 for vc in VehicleClass}
        
        for det in detections:
            vehicle_class = det.get('class')
            if vehicle_class in counts:
                counts[vehicle_class] += 1
        
        return counts
    
    def get_statistics(self, detections: List[Dict]) -> Dict:
        """
        Get statistics about detected vehicles
        
        Args:
            detections: List of vehicle detections
            
        Returns:
            Dictionary with statistics
        """
        if not detections:
            return {
                'total_vehicles': 0,
                'by_class': {vc.value: 0 for vc in VehicleClass},
                'average_confidence': 0.0
            }
        
        counts = self.count_by_class(detections)
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
        
        return {
            'total_vehicles': len(detections),
            'by_class': {vc.value: count for vc, count in counts.items()},
            'average_confidence': avg_confidence
        }
