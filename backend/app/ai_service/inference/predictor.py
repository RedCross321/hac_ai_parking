"""
Main Prediction Pipeline

Orchestrates the complete parking detection and vehicle classification workflow.
"""

import logging
import time
from typing import Optional, Union
from datetime import datetime
import numpy as np

from ..config import AIConfig, DetectionResult, ParkingSpaceStatus, VehicleClass
from ..preprocess import ImageProcessor
from ..models import ParkingDetector, VehicleClassifier

logger = logging.getLogger(__name__)


class ParkingPredictor:
    """
    Main prediction pipeline for parking analysis
    
    Integrates:
    - Image preprocessing
    - Vehicle detection and classification
    - Parking space detection
    - Occupancy analysis
    
    According to README.md v1.2 requirements:
    - Returns free_spaces count
    - Returns vehicle distribution by class (A/B/C/D/PICKUP)
    - Performance target: p95 <= 2 seconds
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """
        Initialize prediction pipeline
        
        Args:
            config: AI configuration parameters
        """
        self.config = config or AIConfig()
        
        # Initialize components
        self.image_processor = ImageProcessor(self.config)
        self.parking_detector = ParkingDetector(self.config)
        self.vehicle_classifier = VehicleClassifier(self.config)
        
        # State
        self.is_ready = False
        
    def initialize(self, 
                   detection_model_path: Optional[str] = None,
                   classifier_model_path: Optional[str] = None,
                   parking_model_path: Optional[str] = None):
        """
        Initialize all models
        
        Args:
            detection_model_path: Path to vehicle detection model
            classifier_model_path: Path to vehicle classifier model
            parking_model_path: Path to parking space detector model
        """
        try:
            logger.info("Initializing parking predictor...")
            
            # Load models
            self.vehicle_classifier.load_model(
                detection_model_path=detection_model_path,
                classifier_model_path=classifier_model_path
            )
            
            self.parking_detector.load_model(parking_model_path)
            
            self.is_ready = True
            logger.info("Parking predictor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize predictor: {e}")
            if self.config.fallback_to_heuristics:
                logger.warning("Continuing with heuristic-only mode")
                self.is_ready = True
            else:
                raise
    
    def predict(
        self,
        image_source: Union[bytes, str, np.ndarray],
        camera_id: str = "unknown",
        timestamp: Optional[str] = None
    ) -> DetectionResult:
        """
        Run complete parking analysis pipeline
        
        Args:
            image_source: Image data (bytes, path, or array)
            camera_id: Camera identifier
            timestamp: Analysis timestamp (auto-generated if not provided)
            
        Returns:
            DetectionResult with parking analysis
        """
        start_time = time.time()
        timestamp = timestamp or datetime.utcnow().isoformat()
        
        try:
            # Step 1: Load and preprocess image
            logger.debug(f"Loading image for camera {camera_id}")
            image = self.image_processor.load_image(image_source)
            image_preprocessed, metadata = self.image_processor.preprocess(image)
            
            # Step 2: Detect vehicles
            logger.debug("Detecting vehicles")
            vehicle_detections = self.vehicle_classifier.detect_and_classify(
                image_preprocessed,
                confidence_threshold=self.config.confidence_threshold
            )
            
            # Transform detections back to original coordinates
            vehicle_detections = self.image_processor.postprocess_detections(
                vehicle_detections,
                metadata
            )
            
            # Step 3: Detect parking spaces
            logger.debug("Detecting parking spaces")
            
            # Try to use predefined layout first
            parking_spaces = self.parking_detector.get_camera_layout(camera_id)
            
            if parking_spaces is None:
                parking_spaces = self.parking_detector.detect_spaces(image)
            
            # Step 4: Analyze occupancy
            logger.debug("Analyzing occupancy")
            occupied_spaces = self.parking_detector.analyze_occupancy(
                image,
                parking_spaces,
                vehicle_detections
            )
            
            # Step 5: Aggregate results
            result = self._aggregate_results(
                camera_id=camera_id,
                timestamp=timestamp,
                occupied_spaces=occupied_spaces,
                vehicle_detections=vehicle_detections,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            # Check performance requirement
            if result.processing_time_ms > self.config.max_processing_time_ms:
                logger.warning(
                    f"Processing time {result.processing_time_ms}ms "
                    f"exceeds target {self.config.max_processing_time_ms}ms"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return DetectionResult(
                camera_id=camera_id,
                timestamp=timestamp,
                total_spaces=0,
                free_spaces=0,
                occupied_spaces=0,
                vehicle_classes={vc: 0 for vc in VehicleClass},
                overall_confidence=0.0,
                processing_time_ms=processing_time_ms,
                success=False,
                error_message=str(e)
            )
    
    def _aggregate_results(
        self,
        camera_id: str,
        timestamp: str,
        occupied_spaces: list,
        vehicle_detections: list,
        processing_time_ms: int
    ) -> DetectionResult:
        """Aggregate analysis results into DetectionResult"""
        
        # Count spaces
        total_spaces = len(occupied_spaces)
        occupied_count = sum(1 for s in occupied_spaces if s.get('is_occupied', False))
        free_count = total_spaces - occupied_count
        
        # Count vehicles by class
        vehicle_counts = {vc: 0 for vc in VehicleClass}
        
        for space in occupied_spaces:
            if space.get('is_occupied') and space.get('vehicle_class'):
                vehicle_class = space['vehicle_class']
                if vehicle_class in vehicle_counts:
                    vehicle_counts[vehicle_class] += 1
        
        # Calculate overall confidence
        confidences = [s.get('confidence', 0.0) for s in occupied_spaces]
        overall_confidence = (
            sum(confidences) / len(confidences) 
            if confidences else 0.0
        )
        
        # Build space status objects
        spaces = []
        for space in occupied_spaces:
            space_status = ParkingSpaceStatus(
                space_id=space.get('space_id', 'unknown'),
                is_occupied=space.get('is_occupied', False),
                vehicle_class=space.get('vehicle_class'),
                confidence=space.get('confidence', 0.0),
                bbox=space.get('bbox')
            )
            spaces.append(space_status)
        
        result = DetectionResult(
            camera_id=camera_id,
            timestamp=timestamp,
            total_spaces=total_spaces,
            free_spaces=free_count,
            occupied_spaces=occupied_count,
            vehicle_classes=vehicle_counts,
            overall_confidence=overall_confidence,
            processing_time_ms=processing_time_ms,
            spaces=spaces,
            success=True
        )
        
        logger.info(
            f"Analysis complete for {camera_id}: "
            f"{free_count}/{total_spaces} free, "
            f"{occupied_count} occupied, "
            f"processing time: {processing_time_ms}ms"
        )
        
        return result
    
    def predict_batch(
        self,
        images: list,
        camera_ids: list,
        timestamps: Optional[list] = None
    ) -> list:
        """
        Run prediction on batch of images
        
        Args:
            images: List of image sources
            camera_ids: List of camera IDs
            timestamps: Optional list of timestamps
            
        Returns:
            List of DetectionResult objects
        """
        if timestamps is None:
            timestamps = [None] * len(images)
        
        results = []
        for image, camera_id, timestamp in zip(images, camera_ids, timestamps):
            result = self.predict(image, camera_id, timestamp)
            results.append(result)
        
        return results
    
    def configure_camera_layout(self, camera_id: str, spaces: list):
        """
        Configure predefined parking space layout for a camera
        
        Args:
            camera_id: Camera identifier
            spaces: List of parking space definitions
        """
        self.parking_detector.configure_camera_layout(camera_id, spaces)
        logger.info(f"Configured layout for camera {camera_id} with {len(spaces)} spaces")
    
    def get_model_info(self) -> dict:
        """Get information about loaded models"""
        return {
            'is_ready': self.is_ready,
            'config': {
                'model_name': self.config.model_name,
                'device': self.config.device,
                'confidence_threshold': self.config.confidence_threshold,
                'input_size': self.config.input_image_size
            },
            'vehicle_classifier_initialized': self.vehicle_classifier.is_initialized,
            'parking_detector_initialized': self.parking_detector.is_initialized
        }
