import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional, Union

class ImageProcessor:
    """
    Utility class for image processing operations.
    """
    
    @staticmethod
    def pil_to_opencv(pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV format.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            OpenCV image array (BGR format)
        """
        # Convert PIL image to RGB if it's not already
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array and change RGB to BGR
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    @staticmethod
    def opencv_to_pil(opencv_image: np.ndarray) -> Image.Image:
        """
        Convert OpenCV image to PIL format.
        
        Args:
            opencv_image: OpenCV image array (BGR format)
            
        Returns:
            PIL Image object
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        return pil_image
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 1024, max_height: int = 768) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: Input image
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized
        
        return image
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better detection.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        
        # Merge channels back
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_image
    
    @staticmethod
    def calculate_image_stats(image: np.ndarray) -> dict:
        """
        Calculate basic image statistics.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with image statistics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        stats = {
            'shape': image.shape,
            'mean_brightness': np.mean(gray),
            'std_brightness': np.std(gray),
            'min_brightness': np.min(gray),
            'max_brightness': np.max(gray),
            'contrast': np.std(gray) / np.mean(gray) if np.mean(gray) > 0 else 0
        }
        
        return stats
    
    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        """
        Convert OpenCV image to base64 string.
        
        Args:
            image: OpenCV image
            
        Returns:
            Base64 encoded string
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64

class ValidationUtils:
    """
    Utility class for validation operations.
    """
    
    @staticmethod
    def validate_image_file(uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded image file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False, "File size too large (max 10MB)"
        
        # Check file extension
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        file_extension = uploaded_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return False, f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        
        try:
            # Try to open the image
            image = Image.open(uploaded_file)
            image.verify()  # Verify it's a valid image
            return True, ""
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def validate_detection_parameters(sensitivity: float, min_area: int) -> Tuple[bool, str]:
        """
        Validate detection parameters.
        
        Args:
            sensitivity: Detection sensitivity value
            min_area: Minimum area value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not 0.1 <= sensitivity <= 1.0:
            return False, "Sensitivity must be between 0.1 and 1.0"
        
        if not 50 <= min_area <= 10000:
            return False, "Minimum area must be between 50 and 10000 pixels"
        
        return True, ""

def format_confidence(confidence: float) -> str:
    """
    Format confidence score for display.
    
    Args:
        confidence: Confidence value (0.0 to 1.0)
        
    Returns:
        Formatted confidence string
    """
    return f"{confidence:.1%}"

def format_area(area: float) -> str:
    """
    Format area for display.
    
    Args:
        area: Area in square pixels
        
    Returns:
        Formatted area string
    """
    if area >= 1000:
        return f"{area/1000:.1f}K px²"
    else:
        return f"{int(area)} px²"

def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level.
    
    Args:
        severity: Severity level string
        
    Returns:
        Color code string
    """
    colors = {
        'Critical': '#FF0000',
        'High': '#FF8C00',
        'Medium': '#FFD700',
        'Low': '#32CD32'
    }
    return colors.get(severity, '#808080')

def calculate_detection_summary(detections: list) -> dict:
    """
    Calculate summary statistics for detections.
    
    Args:
        detections: List of detection dictionaries
        
    Returns:
        Summary statistics dictionary
    """
    if not detections:
        return {
            'total_count': 0,
            'total_area': 0,
            'avg_confidence': 0,
            'max_confidence': 0,
            'severity_distribution': {}
        }
    
    total_area = sum(d['area'] for d in detections)
    confidences = [d['confidence'] for d in detections]
    severities = [d['severity'] for d in detections]
    
    severity_counts = {}
    for severity in severities:
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        'total_count': len(detections),
        'total_area': total_area,
        'avg_confidence': np.mean(confidences),
        'max_confidence': np.max(confidences),
        'severity_distribution': severity_counts
    }
