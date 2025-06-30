# Pipeline Corrosion Detection System

## Overview

This is an AI-powered web application for detecting corrosion on subsea and cross-country oil & gas pipelines. The system uses computer vision techniques to analyze pipeline images and identify potential corrosion areas, providing comprehensive reports for maintenance planning.

The application is built with Streamlit for the web interface and leverages OpenCV for image processing and computer vision algorithms. It provides specialized detection models optimized for different pipeline environments (subsea vs. cross-country).

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Interface**: Single-page application with sidebar controls
- **Session Management**: Streamlit session state for maintaining detection results and processed images
- **Layout**: Wide layout with expandable sidebar for detection settings

### Backend Architecture
- **Core Engine**: Python-based computer vision pipeline
- **Detection Algorithm**: Custom CorrosionDetector class using OpenCV
- **Report Generation**: ReportGenerator class for creating detailed inspection reports
- **Image Processing**: Utility classes for image format conversion and processing

### Key Processing Components
1. **Image Upload and Preprocessing**: PIL/OpenCV integration for image handling
2. **Corrosion Detection**: HSV color space analysis and texture detection
3. **Results Visualization**: Matplotlib-based visualization with bounding boxes
4. **Report Generation**: Comprehensive PDF-ready reports with recommendations

## Key Components

### CorrosionDetector (`corrosion_detector.py`)
- **Purpose**: Core AI detection engine for identifying corrosion in pipeline images
- **Features**:
  - Pipeline-type specific detection (subsea, cross-country, general)
  - Configurable sensitivity and minimum area thresholds
  - HSV color space analysis for rust detection
  - Texture analysis capabilities
- **Detection Methods**:
  - Color-based detection using HSV ranges
  - Morphological operations for noise reduction
  - Contour analysis for corrosion area identification

### ReportGenerator (`report_generator.py`)
- **Purpose**: Generate professional inspection reports
- **Features**:
  - Multiple report types (Executive, Technical, Compliance)
  - Structured report templates
  - Risk assessment and recommendations
  - Detailed findings documentation

### ImageProcessor (`utils.py`)
- **Purpose**: Image processing utilities and format conversions
- **Features**:
  - PIL to OpenCV format conversion
  - Image resizing and optimization
  - Base64 encoding for web display
  - Confidence score formatting

### Main Application (`app.py`)
- **Purpose**: Streamlit web interface and application orchestration
- **Features**:
  - File upload handling
  - Real-time detection parameter adjustment
  - Results visualization and display
  - Report generation interface

## Data Flow

1. **Image Upload**: User uploads pipeline image through Streamlit interface
2. **Preprocessing**: Image is converted to appropriate format and resized if needed
3. **Detection Configuration**: User selects pipeline type and detection sensitivity
4. **Corrosion Analysis**: CorrosionDetector processes image using computer vision algorithms
5. **Results Processing**: Detection results are formatted and visualized
6. **Report Generation**: Comprehensive report is generated based on findings
7. **Output Display**: Results, annotated images, and reports are displayed to user

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **OpenCV (cv2)**: Computer vision and image processing
- **NumPy**: Numerical computing for image arrays
- **PIL (Pillow)**: Image handling and format conversion
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Visualization and plotting

### Additional Dependencies
- **Base64**: Image encoding for web display
- **DateTime**: Timestamp generation for reports
- **IO**: In-memory file operations
- **OS**: File system operations
- **JSON**: Data serialization for reports
- **Math**: Mathematical operations for detection algorithms

## Deployment Strategy

### Development Environment
- **Platform**: Replit-compatible Python environment
- **Requirements**: All dependencies available through pip
- **Configuration**: Streamlit configuration in app.py
- **File Structure**: Modular design with separate concerns

### Production Considerations
- **Scalability**: Single-user application suitable for small to medium workloads
- **Storage**: No persistent storage implemented (session-based)
- **Performance**: Image processing optimized for web deployment
- **Security**: No authentication system currently implemented

### Potential Enhancements
- **Database Integration**: Add Postgres for storing detection history
- **User Authentication**: Implement user management system
- **API Endpoints**: Add REST API for programmatic access
- **Cloud Storage**: Integrate with cloud storage for image persistence

## Changelog

```
Changelog:
- June 30, 2025. Initial setup
- June 30, 2025. Fixed deprecated Streamlit parameters (use_column_width → use_container_width)
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```