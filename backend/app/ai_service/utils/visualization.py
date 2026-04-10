"""
Visualization Utilities

Helper functions for visualizing parking detection results.
"""

import logging
from typing import Optional, List, Tuple
import numpy as np

from ..config import VehicleClass

logger = logging.getLogger(__name__)


class VisualizationHelper:
    """
    Visualization helper for parking detection results
    
    Provides methods to draw:
    - Parking space bounding boxes
    - Vehicle detections
    - Occupancy status
    - Class labels
    """
    
    # Color mapping for vehicle classes
    CLASS_COLORS = {
        VehicleClass.A: (0, 255, 0),      # Green
        VehicleClass.B: (128, 255, 0),    # Lime-green
        VehicleClass.C: (255, 255, 0),    # Yellow
        VehicleClass.D: (255, 128, 0),    # Orange
        VehicleClass.PICKUP: (255, 0, 0), # Red
    }
    
    # Status colors
    COLOR_FREE = (0, 255, 0)      # Green
    COLOR_OCCUPIED = (0, 0, 255)  # Red
    COLOR_UNKNOWN = (128, 128, 128)  # Gray
    
    def __init__(self):
        """Initialize visualization helper"""
        self.font_scale = 0.5
        self.line_thickness = 2
        
    def draw_detections(
        self,
        image: np.ndarray,
        spaces: Optional[List[dict]] = None,
        vehicles: Optional[List[dict]] = None,
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Draw detections on image
        
        Args:
            image: Input image (will be copied)
            spaces: Parking space detections
            vehicles: Vehicle detections
            show_labels: Whether to show class labels
            show_confidence: Whether to show confidence scores
            
        Returns:
            Image with drawn detections
        """
        try:
            import cv2
        except ImportError:
            logger.warning("OpenCV not available, returning original image")
            return image
        
        # Create a copy
        vis_image = image.copy()
        
        # Draw parking spaces
        if spaces:
            vis_image = self._draw_spaces(
                vis_image, spaces, show_labels, show_confidence
            )
        
        # Draw vehicles
        if vehicles:
            vis_image = self._draw_vehicles(
                vis_image, vehicles, show_labels, show_confidence
            )
        
        return vis_image
    
    def _draw_spaces(
        self,
        image: np.ndarray,
        spaces: List[dict],
        show_labels: bool,
        show_confidence: bool
    ) -> np.ndarray:
        """Draw parking space bounding boxes"""
        import cv2
        
        for space in spaces:
            bbox = space.get('bbox')
            if not bbox:
                continue
            
            x1, y1, x2, y2 = map(int, bbox)
            is_occupied = space.get('is_occupied', False)
            confidence = space.get('confidence', 0.0)
            
            # Choose color based on occupancy
            if is_occupied:
                color = self.COLOR_OCCUPIED
            else:
                color = self.COLOR_FREE
            
            # Draw rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), color, self.line_thickness)
            
            # Draw label
            if show_labels:
                label = "OCCUPIED" if is_occupied else "FREE"
                if show_confidence:
                    label += f" {confidence:.2f}"
                
                self._draw_label(image, (x1, y1), label, color)
        
        return image
    
    def _draw_vehicles(
        self,
        image: np.ndarray,
        vehicles: List[dict],
        show_labels: bool,
        show_confidence: bool
    ) -> np.ndarray:
        """Draw vehicle detections with class labels"""
        import cv2
        
        for vehicle in vehicles:
            bbox = vehicle.get('bbox')
            if not bbox:
                continue
            
            x1, y1, x2, y2 = map(int, bbox)
            vehicle_class = vehicle.get('class', VehicleClass.B)
            confidence = vehicle.get('confidence', 0.0)
            
            # Get color for vehicle class
            color = self.CLASS_COLORS.get(vehicle_class, (128, 128, 128))
            
            # Draw rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), color, self.line_thickness)
            
            # Draw label
            if show_labels:
                label = f"{vehicle_class.value}"
                if show_confidence:
                    label += f" {confidence:.2f}"
                
                self._draw_label(image, (x1, y1), label, color)
        
        return image
    
    def _draw_label(
        self,
        image: np.ndarray,
        position: Tuple[int, int],
        text: str,
        color: Tuple[int, int, int]
    ) -> np.ndarray:
        """Draw text label on image"""
        import cv2
        
        x, y = position
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, self.font_scale, self.line_thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            image,
            (x, y - text_height - baseline - 5),
            (x + text_width, y),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            image,
            text,
            (x, y - baseline - 2),
            font,
            self.font_scale,
            (0, 0, 0),
            self.line_thickness
        )
        
        return image
    
    def create_summary_overlay(
        self,
        image: np.ndarray,
        total_spaces: int,
        free_spaces: int,
        occupied_spaces: int,
        vehicle_counts: dict
    ) -> np.ndarray:
        """
        Create summary overlay with statistics
        
        Args:
            image: Input image
            total_spaces: Total number of spaces
            free_spaces: Number of free spaces
            occupied_spaces: Number of occupied spaces
            vehicle_counts: Dictionary of vehicle counts by class
            
        Returns:
            Image with summary overlay
        """
        import cv2
        
        vis_image = image.copy()
        height, width = vis_image.shape[:2]
        
        # Create semi-transparent overlay
        overlay = vis_image.copy()
        
        # Background for stats panel
        panel_height = int(height * 0.15)
        cv2.rectangle(
            overlay,
            (0, 0),
            (width, panel_height),
            (0, 0, 0),
            -1
        )
        
        # Blend overlay
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, vis_image, 1 - alpha, 0, vis_image)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        
        y_offset = 30
        x_offset = 20
        
        # Title
        cv2.putText(
            vis_image,
            "Parking Analysis",
            (x_offset, y_offset),
            font,
            font_scale,
            (255, 255, 255),
            2
        )
        
        y_offset += 25
        
        # Space counts
        cv2.putText(
            vis_image,
            f"Total: {total_spaces} | Free: {free_spaces} | Occupied: {occupied_spaces}",
            (x_offset, y_offset),
            font,
            font_scale * 0.9,
            (255, 255, 255),
            1
        )
        
        y_offset += 25
        
        # Vehicle distribution
        vehicle_str = " | ".join([
            f"{cls}: {count}" 
            for cls, count in vehicle_counts.items() 
            if count > 0
        ])
        
        if vehicle_str:
            cv2.putText(
                vis_image,
                f"Vehicles: {vehicle_str}",
                (x_offset, y_offset),
                font,
                font_scale * 0.8,
                (200, 200, 200),
                1
            )
        
        return vis_image
    
    def draw_comparison(
        self,
        original_image: np.ndarray,
        processed_image: np.ndarray
    ) -> np.ndarray:
        """
        Draw side-by-side comparison of original and processed images
        
        Args:
            original_image: Original input image
            processed_image: Processed/detected image
            
        Returns:
            Combined comparison image
        """
        import cv2
        
        # Ensure same size
        height, width = original_image.shape[:2]
        processed_resized = cv2.resize(processed_image, (width, height))
        
        # Combine horizontally
        combined = np.hstack([original_image, processed_resized])
        
        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            combined,
            "Original",
            (20, 30),
            font,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            combined,
            "Processed",
            (width + 20, 30),
            font,
            0.7,
            (255, 255, 255),
            2
        )
        
        return combined
