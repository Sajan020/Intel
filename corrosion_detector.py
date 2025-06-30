import cv2
import numpy as np
from typing import List, Dict, Tuple, Any
import math

class CorrosionDetector:
    """
    AI-powered corrosion detection system for pipeline images.
    Uses computer vision techniques to identify potential corrosion areas.
    """
    
    def __init__(self, sensitivity: float = 0.5, min_area: int = 200, pipeline_type: str = "unknown"):
        """
        Initialize the corrosion detector.
        
        Args:
            sensitivity: Detection sensitivity (0.1 to 1.0)
            min_area: Minimum area in pixels to consider as corrosion
            pipeline_type: Type of pipeline (subsea, cross-country, unknown)
        """
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.pipeline_type = pipeline_type
        
        # Adjust parameters based on pipeline type
        if pipeline_type == "subsea":
            self.rust_color_ranges = self._get_subsea_color_ranges()
            self.texture_sensitivity = 0.7
        elif pipeline_type == "cross-country":
            self.rust_color_ranges = self._get_cross_country_color_ranges()
            self.texture_sensitivity = 0.6
        else:
            self.rust_color_ranges = self._get_general_color_ranges()
            self.texture_sensitivity = 0.65
    
    def _get_subsea_color_ranges(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Get color ranges optimized for subsea pipeline corrosion detection."""
        return [
            # Orange-brown rust (common in marine environments)
            (np.array([5, 50, 50]), np.array([15, 255, 255])),
            # Reddish-brown rust
            (np.array([0, 50, 50]), np.array([10, 255, 255])),
            # Dark rust/oxidation
            (np.array([10, 50, 20]), np.array([25, 255, 150])),
        ]
    
    def _get_cross_country_color_ranges(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Get color ranges optimized for cross-country pipeline corrosion detection."""
        return [
            # Standard rust colors for atmospheric corrosion
            (np.array([5, 70, 50]), np.array([15, 255, 255])),
            # Reddish rust
            (np.array([0, 60, 50]), np.array([10, 255, 255])),
            # Brown oxidation
            (np.array([10, 50, 30]), np.array([20, 255, 200])),
        ]
    
    def _get_general_color_ranges(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Get general color ranges for corrosion detection."""
        return [
            # Orange rust
            (np.array([5, 50, 50]), np.array([15, 255, 255])),
            # Red rust
            (np.array([0, 50, 50]), np.array([10, 255, 255])),
            # Brown rust
            (np.array([10, 50, 30]), np.array([25, 255, 200])),
            # Yellow-brown rust
            (np.array([15, 50, 50]), np.array([30, 255, 255])),
        ]
    
    def detect_corrosion(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detect corrosion in the input image.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Dictionary containing detection results
        """
        # Preprocess the image
        preprocessed = self._preprocess_image(image)
        
        # Detect corrosion using multiple methods
        color_mask = self._detect_by_color(preprocessed)
        texture_mask = self._detect_by_texture(preprocessed)
        edge_mask = self._detect_by_edges(preprocessed)
        
        # Combine detection methods
        combined_mask = self._combine_detections(color_mask, texture_mask, edge_mask)
        
        # Find and filter contours
        contours = self._find_contours(combined_mask)
        filtered_contours = self._filter_contours(contours)
        
        # Analyze detections
        detections = self._analyze_detections(filtered_contours, image)
        
        # Create annotated image
        annotated_image = self._create_annotated_image(image.copy(), detections)
        
        return {
            'detections': detections,
            'annotated_image': annotated_image,
            'masks': {
                'color': color_mask,
                'texture': texture_mask,
                'edge': edge_mask,
                'combined': combined_mask
            }
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for better detection accuracy."""
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply slight Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab_l, lab_a, lab_b = cv2.split(lab)
        lab_l = clahe.apply(lab_l)
        enhanced_lab = cv2.merge([lab_l, lab_a, lab_b])
        enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_image
    
    def _detect_by_color(self, image: np.ndarray) -> np.ndarray:
        """Detect corrosion based on color characteristics."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask for rust colors
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in self.rust_color_ranges:
            color_mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.bitwise_or(mask, color_mask)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _detect_by_texture(self, image: np.ndarray) -> np.ndarray:
        """Detect corrosion based on texture characteristics."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use Local Binary Pattern-like texture analysis
        # Calculate standard deviation in local neighborhoods
        kernel = np.ones((9, 9), np.float32) / 81
        mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        sqr_mean = cv2.filter2D((gray.astype(np.float32))**2, -1, kernel)
        std_dev = np.sqrt(sqr_mean - mean**2)
        
        # Normalize and threshold
        std_dev_norm = ((std_dev - std_dev.min()) / (std_dev.max() - std_dev.min()) * 255).astype(np.uint8)
        
        # Threshold based on texture sensitivity
        threshold_value = int(255 * (1 - self.texture_sensitivity))
        _, texture_mask = cv2.threshold(std_dev_norm, threshold_value, 255, cv2.THRESH_BINARY)
        
        return texture_mask
    
    def _detect_by_edges(self, image: np.ndarray) -> np.ndarray:
        """Detect corrosion based on edge characteristics."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to create regions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edge_mask = cv2.dilate(edges, kernel, iterations=2)
        
        return edge_mask
    
    def _combine_detections(self, color_mask: np.ndarray, texture_mask: np.ndarray, edge_mask: np.ndarray) -> np.ndarray:
        """Combine different detection methods."""
        # Weight the different methods based on sensitivity
        weighted_color = (color_mask * 0.5).astype(np.uint8)
        weighted_texture = (texture_mask * 0.3).astype(np.uint8)
        weighted_edge = (edge_mask * 0.2).astype(np.uint8)
        
        # Combine masks
        combined = cv2.add(cv2.add(weighted_color, weighted_texture), weighted_edge)
        
        # Apply sensitivity threshold
        threshold = int(255 * (1 - self.sensitivity))
        _, combined_mask = cv2.threshold(combined, threshold, 255, cv2.THRESH_BINARY)
        
        # Clean up the combined mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        return combined_mask
    
    def _find_contours(self, mask: np.ndarray) -> List[np.ndarray]:
        """Find contours in the detection mask."""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def _filter_contours(self, contours: List[np.ndarray]) -> List[np.ndarray]:
        """Filter contours based on area and shape characteristics."""
        filtered = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum area
            if area < self.min_area:
                continue
            
            # Filter by aspect ratio (avoid very thin lines)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(w, h) / min(w, h)
            if aspect_ratio > 10:  # Skip very elongated shapes
                continue
            
            # Filter by extent (area/bounding_rect_area)
            extent = area / (w * h)
            if extent < 0.1:  # Skip very sparse contours
                continue
            
            filtered.append(contour)
        
        return filtered
    
    def _analyze_detections(self, contours: List[np.ndarray], original_image: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze detected contours and extract features."""
        detections = []
        
        for i, contour in enumerate(contours):
            # Basic measurements
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate features
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            aspect_ratio = max(w, h) / min(w, h)
            extent = area / (w * h)
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(contour, original_image, area, circularity, extent)
            
            # Determine severity based on area and confidence
            severity = self._determine_severity(area, confidence)
            
            # Risk assessment
            risk_assessment = self._assess_risk(area, confidence, severity)
            
            detection = {
                'id': i + 1,
                'bbox': [x, y, w, h],
                'area': int(area),
                'perimeter': int(perimeter),
                'circularity': round(circularity, 3),
                'aspect_ratio': round(aspect_ratio, 2),
                'extent': round(extent, 3),
                'confidence': confidence,
                'severity': severity,
                'risk_assessment': risk_assessment,
                'contour': contour
            }
            
            detections.append(detection)
        
        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detections
    
    def _calculate_confidence(self, contour: np.ndarray, image: np.ndarray, area: float, 
                            circularity: float, extent: float) -> float:
        """Calculate confidence score for a detection."""
        # Extract region of interest
        x, y, w, h = cv2.boundingRect(contour)
        roi = image[y:y+h, x:x+w]
        
        if roi.size == 0:
            return 0.0
        
        # Analyze color characteristics
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Check how much of the ROI matches rust colors
        color_score = 0
        total_pixels = roi.shape[0] * roi.shape[1]
        
        for lower, upper in self.rust_color_ranges:
            mask = cv2.inRange(hsv_roi, lower, upper)
            matching_pixels = np.sum(mask > 0)
            color_score += matching_pixels / total_pixels
        
        color_score = min(color_score, 1.0)  # Cap at 1.0
        
        # Shape characteristics score
        shape_score = 0.5  # Base score
        
        # Prefer more circular/irregular shapes (typical of corrosion)
        if 0.3 <= circularity <= 0.8:
            shape_score += 0.2
        
        # Prefer reasonable extent values
        if 0.3 <= extent <= 0.9:
            shape_score += 0.2
        
        # Size score (larger areas are more likely to be corrosion)
        size_score = min(area / 2000, 1.0)  # Normalize to max area of 2000px
        
        # Combine scores
        confidence = (color_score * 0.5 + shape_score * 0.3 + size_score * 0.2)
        
        return max(0.0, min(1.0, confidence))
    
    def _determine_severity(self, area: float, confidence: float) -> str:
        """Determine severity level based on area and confidence."""
        # Severity thresholds (can be adjusted based on requirements)
        if area > 5000 and confidence > 0.8:
            return "Critical"
        elif area > 2000 and confidence > 0.6:
            return "High"
        elif area > 800 and confidence > 0.4:
            return "Medium"
        else:
            return "Low"
    
    def _assess_risk(self, area: float, confidence: float, severity: str) -> str:
        """Assess risk level for maintenance planning."""
        if severity == "Critical":
            return "Immediate action required"
        elif severity == "High":
            return "Schedule maintenance within 30 days"
        elif severity == "Medium":
            return "Monitor and schedule maintenance within 90 days"
        else:
            return "Monitor during next routine inspection"
    
    def _create_annotated_image(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Create annotated image with bounding boxes and labels."""
        # Define colors for different severity levels
        severity_colors = {
            "Critical": (0, 0, 255),      # Red
            "High": (0, 165, 255),        # Orange
            "Medium": (0, 255, 255),      # Yellow
            "Low": (0, 255, 0)            # Green
        }
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            severity = detection['severity']
            confidence = detection['confidence']
            
            # Get color for severity
            color = severity_colors.get(severity, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Draw filled rectangle for label background
            label_text = f"{severity} ({confidence:.1%})"
            label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            cv2.rectangle(image, (x, y - label_size[1] - 10), 
                         (x + label_size[0] + 10, y), color, -1)
            
            # Draw label text
            cv2.putText(image, label_text, (x + 5, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw detection ID
            id_text = f"C{detection['id']:03d}"
            cv2.putText(image, id_text, (x + 5, y + h - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
