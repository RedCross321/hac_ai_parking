"""
AI Service for Parking Detection and Vehicle Classification

This module provides AI-powered analysis of parking lot images to detect:
1. Number of free parking spaces
2. Vehicle classes (A/B/C/D/PICKUP) for occupied spaces
"""

__version__ = "0.1.0"
__author__ = "hac_ai_parking team"

from .config import AIConfig, VehicleClass

__all__ = ["AIConfig", "VehicleClass"]
