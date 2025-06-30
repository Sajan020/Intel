import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os

from corrosion_detector import CorrosionDetector
from report_generator import ReportGenerator
from utils import ImageProcessor, format_confidence

# Configure page
st.set_page_config(
    page_title="Pipeline Corrosion Detection System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None

def main():
    st.title("🔧 AI-Powered Pipeline Corrosion Detection System")
    st.markdown("### Detect corrosion on subsea and cross-country oil & gas pipelines")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Detection Settings")
        
        # Pipeline type selection
        pipeline_type = st.selectbox(
            "Pipeline Type",
            ["Subsea", "Cross-Country", "Unknown"],
            help="Select the pipeline environment type for optimized detection"
        )
        
        # Detection sensitivity
        sensitivity = st.slider(
            "Detection Sensitivity",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher values detect more potential corrosion spots (may increase false positives)"
        )
        
        # Minimum corrosion area
        min_area = st.slider(
            "Minimum Corrosion Area (pixels)",
            min_value=50,
            max_value=1000,
            value=200,
            step=50,
            help="Minimum area size to consider as corrosion"
        )
        
        st.markdown("---")
        st.markdown("**System Info**")
        st.info("This system uses computer vision algorithms to detect potential corrosion areas in pipeline images.")
        
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Pipeline Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a high-resolution image of the pipeline for corrosion analysis"
        )
        
        if uploaded_file is not None:
            # Load and display original image
            image = Image.open(uploaded_file)
            st.session_state.original_image = image
            
            st.subheader("Original Image")
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
            
            # Image info
            st.markdown(f"**Image Details:**")
            st.markdown(f"- Size: {image.size[0]} x {image.size[1]} pixels")
            st.markdown(f"- Format: {image.format}")
            st.markdown(f"- Mode: {image.mode}")
            
            # Process image button
            if st.button("🔍 Detect Corrosion", type="primary", use_container_width=True):
                with st.spinner("Analyzing image for corrosion..."):
                    # Initialize detector
                    detector = CorrosionDetector(
                        sensitivity=sensitivity,
                        min_area=min_area,
                        pipeline_type=pipeline_type.lower()
                    )
                    
                    # Convert PIL to OpenCV format
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Detect corrosion
                    results = detector.detect_corrosion(opencv_image)
                    
                    # Store results in session state
                    st.session_state.detection_results = results
                    st.session_state.processed_image = results['annotated_image']
                    
                st.success("Analysis complete!")
                st.rerun()
    
    with col2:
        st.header("🔍 Detection Results")
        
        if st.session_state.detection_results is not None:
            results = st.session_state.detection_results
            
            # Display processed image
            st.subheader("Detected Corrosion Areas")
            processed_image_rgb = cv2.cvtColor(st.session_state.processed_image, cv2.COLOR_BGR2RGB)
            st.image(processed_image_rgb, caption="Corrosion Detection Results", use_container_width=True)
            
            # Detection summary
            st.subheader("📊 Detection Summary")
            
            # Calculate severity counts
            severity_counts = {}
            for detection in results['detections']:
                severity = detection['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            col_summary1, col_summary2, col_summary3 = st.columns(3)
            
            with col_summary1:
                st.metric(
                    label="Corrosion Spots",
                    value=len(results['detections'])
                )
            
            with col_summary2:
                avg_confidence = np.mean([d['confidence'] for d in results['detections']]) if results['detections'] else 0
                st.metric(
                    label="Avg. Confidence",
                    value=f"{avg_confidence:.1%}"
                )
                
                max_severity = "None"
                if severity_counts:
                    severity_order = ['Low', 'Medium', 'High', 'Critical']
                    for sev in reversed(severity_order):
                        if sev in severity_counts:
                            max_severity = sev
                            break
                
                color = {
                    "None": "normal",
                    "Low": "normal", 
                    "Medium": "normal",
                    "High": "inverse",
                    "Critical": "inverse"
                }.get(max_severity, "normal")
                
                st.metric(
                    label="Max Severity",
                    value=max_severity
                )
        else:
            st.info("Upload an image and click 'Detect Corrosion' to see results here.")
    
    # Detailed results section
    if st.session_state.detection_results is not None:
        st.markdown("---")
        st.header("📋 Detailed Analysis")
        
        results = st.session_state.detection_results
        
        if results['detections']:
            # Create detailed table
            detection_data = []
            for i, detection in enumerate(results['detections'], 1):
                detection_data.append({
                    'ID': f"C{i:03d}",
                    'Location (x, y)': f"({detection['bbox'][0]}, {detection['bbox'][1]})",
                    'Size (w × h)': f"{detection['bbox'][2]} × {detection['bbox'][3]}",
                    'Area (px²)': detection['area'],
                    'Confidence': format_confidence(detection['confidence']),
                    'Severity': detection['severity'],
                    'Risk Level': detection['risk_assessment']
                })
            
            df = pd.DataFrame(detection_data)
            st.dataframe(df, use_container_width=True)
            
            # Generate and download report
            st.subheader("📄 Generate Report")
            
            col_report1, col_report2 = st.columns(2)
            
            with col_report1:
                inspector_name = st.text_input("Inspector Name", value="Field Engineer")
                location = st.text_input("Pipeline Location", value="Pipeline Section A")
            
            with col_report2:
                inspection_date = st.date_input("Inspection Date", value=datetime.now().date())
                report_type = st.selectbox("Report Type", ["Summary", "Detailed", "Technical"])
            
            if st.button("📄 Generate Report", type="secondary"):
                report_generator = ReportGenerator()
                
                # Recalculate severity counts for report
                report_severity_counts = {}
                for detection in results['detections']:
                    severity = detection['severity']
                    report_severity_counts[severity] = report_severity_counts.get(severity, 0) + 1
                
                report_data = {
                    'inspector_name': inspector_name,
                    'location': location,
                    'inspection_date': inspection_date.strftime("%Y-%m-%d"),
                    'pipeline_type': pipeline_type,
                    'report_type': report_type,
                    'image_name': uploaded_file.name if uploaded_file else "unknown.jpg",
                    'detections': results['detections'],
                    'total_detections': len(results['detections']),
                    'avg_confidence': np.mean([d['confidence'] for d in results['detections']]) if results['detections'] else 0,
                    'severity_counts': report_severity_counts
                }
                
                report_content = report_generator.generate_report(report_data)
                
                # Provide download button
                st.download_button(
                    label="📥 Download Report",
                    data=report_content,
                    file_name=f"corrosion_report_{inspection_date.strftime('%Y%m%d')}_{location.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
                
                st.success("Report generated successfully!")
        else:
            st.info("No corrosion detected in the uploaded image.")
            
            # Still allow report generation for clean inspections
            st.subheader("📄 Generate Clean Inspection Report")
            
            col_clean1, col_clean2 = st.columns(2)
            
            with col_clean1:
                inspector_name = st.text_input("Inspector Name", value="Field Engineer", key="clean_inspector")
                location = st.text_input("Pipeline Location", value="Pipeline Section A", key="clean_location")
            
            with col_clean2:
                inspection_date = st.date_input("Inspection Date", value=datetime.now().date(), key="clean_date")
            
            if st.button("📄 Generate Clean Report", type="secondary"):
                report_generator = ReportGenerator()
                
                report_data = {
                    'inspector_name': inspector_name,
                    'location': location,
                    'inspection_date': inspection_date.strftime("%Y-%m-%d"),
                    'pipeline_type': pipeline_type,
                    'report_type': "Clean Inspection",
                    'image_name': uploaded_file.name if uploaded_file else "unknown.jpg",
                    'detections': [],
                    'total_detections': 0,
                    'avg_confidence': 0,
                    'severity_counts': {}
                }
                
                report_content = report_generator.generate_report(report_data)
                
                st.download_button(
                    label="📥 Download Clean Report",
                    data=report_content,
                    file_name=f"clean_inspection_report_{inspection_date.strftime('%Y%m%d')}_{location.replace(' ', '_')}.txt",
                    mime="text/plain",
                    key="clean_download"
                )
                
                st.success("Clean inspection report generated!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Pipeline Corrosion Detection System | Developed for Industrial Applications</p>
            <p><small>⚠️ This tool provides assistance in corrosion detection. Always verify results with manual inspection.</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
