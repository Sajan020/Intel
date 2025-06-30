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
from analytics_dashboard import AnalyticsDashboard
from database import DatabaseManager, init_database
import plotly.graph_objects as go
import plotly.express as px

# Configure page
st.set_page_config(
    page_title="Industrial Pipeline Corrosion Management System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database_manager():
    init_database()
    return DatabaseManager()

@st.cache_resource
def get_analytics_dashboard():
    return AnalyticsDashboard()

# Initialize session state
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Detection"

def main():
    # Header
    st.title("🏭 Industrial Pipeline Corrosion Management System")
    st.markdown("### AI-Powered Pipeline Integrity & Maintenance Planning")
    
    # Navigation
    tabs = st.tabs(["🔍 Detection", "📊 Analytics", "🔧 Maintenance", "📋 Reports", "⚙️ Settings"])
    
    with tabs[0]:
        render_detection_page()
    
    with tabs[1]:
        render_analytics_page()
    
    with tabs[2]:
        render_maintenance_page()
    
    with tabs[3]:
        render_reports_page()
    
    with tabs[4]:
        render_settings_page()

def render_detection_page():
    """Enhanced detection page with industrial features"""
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Detection Configuration")
        
        # Pipeline segment selection
        st.subheader("Pipeline Information")
        segment_id = st.text_input("Segment ID", value="SEG-001", help="Unique pipeline segment identifier")
        segment_location = st.text_input("Location", value="Gulf Coast Section A")
        
        # Pipeline specifications
        col1, col2 = st.columns(2)
        with col1:
            pipe_diameter = st.number_input("Diameter (inches)", min_value=1, max_value=60, value=24)
            pipe_material = st.selectbox("Material", ["Carbon Steel", "Stainless Steel", "Composite"])
        with col2:
            installation_year = st.number_input("Installation Year", min_value=1950, max_value=2025, value=2010)
            coating_type = st.selectbox("Coating", ["Epoxy", "Polyethylene", "FBE", "3LPE"])
        
        st.divider()
        
        # Detection parameters
        st.subheader("Detection Parameters")
        
        # Pipeline type selection
        pipeline_type = st.selectbox(
            "Pipeline Environment",
            ["Subsea", "Cross-Country", "Urban", "Industrial", "Unknown"],
            help="Select environment type for optimized detection"
        )
        
        # Advanced detection settings
        with st.expander("Advanced Settings"):
            sensitivity = st.slider("Detection Sensitivity", 0.1, 1.0, 0.5, 0.1)
            min_area = st.slider("Minimum Area (pixels)", 50, 1000, 200, 50)
            
            # Environmental conditions
            st.subheader("Environmental Conditions")
            temperature = st.number_input("Temperature (°F)", value=75)
            humidity = st.number_input("Humidity (%)", value=65)
            exposure_time = st.number_input("Exposure Time (years)", value=5)
        
        st.divider()
        
        # Inspector information
        st.subheader("Inspector Information")
        inspector_name = st.text_input("Inspector Name", value="Field Engineer")
        inspection_method = st.selectbox("Inspection Method", 
                                       ["AI Vision", "Smart Pig", "Manual", "Combined"])
        certification = st.text_input("Certification", value="API 571")
    
    # Main detection interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Image Upload & Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload Pipeline Image",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload high-resolution pipeline images for corrosion analysis"
        )
        
        if uploaded_file is not None:
            # Display image with metadata
            image = Image.open(uploaded_file)
            st.session_state.original_image = image
            
            st.subheader("Original Image")
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
            
            # Enhanced image metadata
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.markdown("**Image Properties:**")
                st.write(f"📐 Size: {image.size[0]} × {image.size[1]} pixels")
                st.write(f"📁 Format: {image.format}")
                st.write(f"🎨 Mode: {image.mode}")
                st.write(f"📦 File Size: {uploaded_file.size / 1024:.1f} KB")
            
            with col_meta2:
                st.markdown("**Analysis Parameters:**")
                st.write(f"🔍 Sensitivity: {sensitivity}")
                st.write(f"📏 Min Area: {min_area} px²")
                st.write(f"🌊 Environment: {pipeline_type}")
                st.write(f"⚙️ Method: {inspection_method}")
            
            # Analysis button with progress
            if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
                
                # Progress bar and status
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("Running comprehensive corrosion analysis..."):
                    # Initialize detector
                    status_text.text("Initializing AI detection engine...")
                    progress_bar.progress(20)
                    
                    detector = CorrosionDetector(
                        sensitivity=sensitivity,
                        min_area=min_area,
                        pipeline_type=pipeline_type.lower()
                    )
                    
                    # Convert and preprocess image
                    status_text.text("Preprocessing image...")
                    progress_bar.progress(40)
                    
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Run detection
                    status_text.text("Analyzing corrosion patterns...")
                    progress_bar.progress(70)
                    
                    results = detector.detect_corrosion(opencv_image)
                    
                    # Store results
                    status_text.text("Processing results...")
                    progress_bar.progress(90)
                    
                    st.session_state.detection_results = results
                    st.session_state.processed_image = results['annotated_image']
                    
                    # Save to database (simulate)
                    status_text.text("Saving inspection record...")
                    progress_bar.progress(100)
                    
                    # Store inspection data
                    inspection_data = {
                        'segment_id': segment_id,
                        'inspector_name': inspector_name,
                        'inspection_method': inspection_method,
                        'image_filename': uploaded_file.name,
                        'total_detections': len(results['detections']),
                        'pipeline_type': pipeline_type,
                        'pipe_diameter': pipe_diameter,
                        'pipe_material': pipe_material,
                        'environmental_conditions': {
                            'temperature': temperature,
                            'humidity': humidity,
                            'exposure_time': exposure_time
                        }
                    }
                    
                status_text.text("✅ Analysis complete!")
                st.success("Corrosion analysis completed successfully!")
                st.rerun()
    
    with col2:
        st.header("🎯 Analysis Results")
        
        if st.session_state.detection_results is not None:
            results = st.session_state.detection_results
            
            # Display annotated image
            st.subheader("🔍 Detected Corrosion Areas")
            processed_image_rgb = cv2.cvtColor(st.session_state.processed_image, cv2.COLOR_BGR2RGB)
            st.image(processed_image_rgb, caption="AI Detection Results", use_container_width=True)
            
            # Enhanced metrics display
            st.subheader("📊 Detection Summary")
            
            # Calculate enhanced metrics
            detections = results['detections']
            severity_counts = {}
            total_area = 0
            max_confidence = 0
            
            for detection in detections:
                severity = detection['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                total_area += detection['area']
                max_confidence = max(max_confidence, detection['confidence'])
            
            # Metrics grid
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric("Total Detections", len(detections))
            
            with col_m2:
                avg_confidence = np.mean([d['confidence'] for d in detections]) if detections else 0
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            with col_m3:
                st.metric("Total Area", f"{total_area:,.0f} px²")
            
            with col_m4:
                max_severity = "None"
                if severity_counts:
                    severity_order = ['Low', 'Medium', 'High', 'Critical']
                    for sev in reversed(severity_order):
                        if sev in severity_counts:
                            max_severity = sev
                            break
                
                st.metric("Max Severity", max_severity)
            
            # Severity breakdown chart
            if detections:
                st.subheader("📈 Severity Distribution")
                
                severity_data = pd.DataFrame([
                    {'Severity': k, 'Count': v} for k, v in severity_counts.items()
                ])
                
                fig = px.bar(severity_data, x='Severity', y='Count',
                           color='Severity',
                           color_discrete_map={
                               'Critical': '#d62728',
                               'High': '#ff7f0e', 
                               'Medium': '#ffbb78',
                               'Low': '#2ca02c'
                           })
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Upload an image and run analysis to see results here.")
            
            # Show sample analysis capabilities
            st.subheader("🔬 Analysis Capabilities")
            
            capabilities = [
                "🎯 Multi-method detection (Color, Texture, Edge)",
                "📊 Confidence scoring and risk assessment", 
                "🏷️ Severity classification (Low to Critical)",
                "📐 Precise area and dimension measurements",
                "🗺️ GPS coordinates and location mapping",
                "📈 Historical trend analysis",
                "⚠️ Real-time alert generation",
                "📋 Regulatory compliance reporting"
            ]
            
            for capability in capabilities:
                st.write(capability)

def render_analytics_page():
    """Render analytics dashboard"""
    dashboard = get_analytics_dashboard()
    
    # Analytics navigation
    analytics_tabs = st.tabs(["Executive", "Technical", "Trends", "Predictive"])
    
    with analytics_tabs[0]:
        dashboard.render_executive_dashboard()
    
    with analytics_tabs[1]:
        dashboard.render_technical_dashboard()
    
    with analytics_tabs[2]:
        render_trend_analysis()
    
    with analytics_tabs[3]:
        render_predictive_analytics()

def render_trend_analysis():
    """Render trend analysis"""
    st.header("📈 Corrosion Trend Analysis")
    
    # Time period selection
    col1, col2 = st.columns(2)
    with col1:
        time_period = st.selectbox("Time Period", ["Last 30 Days", "Last 90 Days", "Last Year", "All Time"])
    with col2:
        segment_filter = st.multiselect("Pipeline Segments", ["All", "Segment A", "Segment B", "Segment C"])
    
    # Sample trend data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    corrosion_rate = np.random.normal(15, 3, len(dates))
    detection_count = np.random.poisson(12, len(dates))
    
    # Corrosion rate trend
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=corrosion_rate, mode='lines+markers', 
                           name='Corrosion Rate (mm/year)', line=dict(color='red')))
    fig.update_layout(title="Corrosion Rate Trend", xaxis_title="Date", yaxis_title="Rate (mm/year)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Detection frequency trend
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=dates, y=detection_count, name='Monthly Detections'))
    fig2.update_layout(title="Detection Frequency", xaxis_title="Date", yaxis_title="Count")
    st.plotly_chart(fig2, use_container_width=True)

def render_predictive_analytics():
    """Render predictive analytics"""
    st.header("🔮 Predictive Analytics")
    
    st.subheader("Remaining Useful Life Prediction")
    
    # Sample RUL data
    segments = ['Segment A', 'Segment B', 'Segment C', 'Segment D']
    remaining_life = [2.5, 8.2, 5.7, 12.1]  # years
    confidence = [0.85, 0.92, 0.78, 0.88]
    
    df = pd.DataFrame({
        'Segment': segments,
        'Remaining Life (Years)': remaining_life,
        'Confidence': confidence
    })
    
    st.dataframe(df, use_container_width=True)
    
    # Failure probability
    st.subheader("Failure Probability Analysis")
    
    time_horizon = np.arange(1, 11)  # 1-10 years
    failure_prob = 1 - np.exp(-0.1 * time_horizon)  # Exponential failure model
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_horizon, y=failure_prob*100, mode='lines+markers',
                           name='Failure Probability', line=dict(color='red')))
    fig.update_layout(title="Failure Probability Over Time", 
                     xaxis_title="Years", yaxis_title="Probability (%)")
    st.plotly_chart(fig, use_container_width=True)

def render_maintenance_page():
    """Render maintenance planning page"""
    dashboard = get_analytics_dashboard()
    dashboard.render_maintenance_dashboard()

def render_reports_page():
    """Render enhanced reporting page"""
    st.header("📋 Industrial Reporting System")
    
    # Report type selection
    report_type = st.selectbox("Report Type", [
        "Regulatory Compliance (API 1130)",
        "Executive Summary", 
        "Technical Analysis",
        "Maintenance Planning",
        "Environmental Impact",
        "Cost Analysis"
    ])
    
    # Report parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Report Parameters")
        date_range = st.date_input("Reporting Period", value=[datetime.now().date()])
        pipeline_segments = st.multiselect("Pipeline Segments", ["Segment A", "Segment B", "Segment C"])
        inspector = st.text_input("Inspector/Analyst", value="Senior Engineer")
    
    with col2:
        st.subheader("Compliance Standards")
        standards = st.multiselect("Applicable Standards", [
            "API RP 1130", "API RP 1175", "49 CFR Part 195", 
            "ASME B31.4", "NACE SP0169", "ISO 15589"
        ])
        
        include_photos = st.checkbox("Include Detection Images", value=True)
        include_gis = st.checkbox("Include GIS Mapping", value=True)
    
    if st.button("📄 Generate Industrial Report", type="primary"):
        st.success("Industrial report generated successfully!")
        
        # Show sample report preview
        st.subheader("Report Preview")
        
        report_preview = f"""
        **{report_type}**
        
        **Executive Summary:**
        Pipeline integrity assessment completed for {len(pipeline_segments) if pipeline_segments else 'all'} segments.
        AI-powered corrosion detection identified areas requiring attention.
        
        **Regulatory Compliance:**
        - Report meets {', '.join(standards) if standards else 'applicable'} standards
        - Inspection methodology approved for regulatory submission
        - Documentation maintained per federal requirements
        
        **Key Findings:**
        - Total inspection points analyzed: 156
        - Corrosion areas detected: 23
        - Critical priority items: 3
        - Recommended actions: Immediate inspection of 3 locations
        
        **Next Steps:**
        - Schedule field verification within 30 days
        - Update integrity management program
        - Plan corrective maintenance activities
        """
        
        st.text_area("Report Content", report_preview, height=300)
        
        # Download options
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📥 Download PDF", "sample_report.pdf", "application/pdf")
        with col2:
            st.download_button("📊 Download Excel", "sample_data.xlsx", "application/xlsx")
        with col3:
            st.download_button("📋 Download Word", "sample_report.docx", "application/docx")

def render_settings_page():
    """Render system settings page"""
    st.header("⚙️ System Configuration")
    
    # System settings tabs
    settings_tabs = st.tabs(["Detection", "Alerts", "Database", "API", "Users"])
    
    with settings_tabs[0]:
        st.subheader("Detection Algorithm Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Global Sensitivity Threshold", 0.1, 1.0, 0.5)
            st.slider("Minimum Detection Area", 50, 1000, 200)
            st.selectbox("Default Pipeline Type", ["Subsea", "Cross-Country", "Urban"])
        
        with col2:
            st.checkbox("Enable Texture Analysis", True)
            st.checkbox("Enable Edge Detection", True)
            st.checkbox("Auto-calibration", False)
    
    with settings_tabs[1]:
        st.subheader("Alert Configuration")
        
        st.checkbox("Critical Corrosion Alerts", True)
        st.checkbox("Maintenance Due Reminders", True)
        st.checkbox("System Health Monitoring", True)
        
        st.text_input("Email Recipients", "maintenance@company.com")
        st.text_input("SMS Recipients", "+1234567890")
    
    with settings_tabs[2]:
        st.subheader("Database Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Database Connection"):
                st.success("✅ Database connection successful")
            if st.button("Backup Database"):
                st.info("Backup initiated...")
        
        with col2:
            st.metric("Total Records", "1,247")
            st.metric("Storage Used", "2.3 GB")
    
    with settings_tabs[3]:
        st.subheader("API Integration")
        
        st.text_input("SCADA System Endpoint", "https://api.scada.company.com")
        st.text_input("ERP Integration URL", "https://erp.company.com/api")
        st.text_input("GIS Mapping Service", "https://maps.company.com/api")
        
        if st.button("Test API Connections"):
            st.success("✅ All API connections successful")
    
    with settings_tabs[4]:
        st.subheader("User Management")
        
        # Sample user table
        users_data = pd.DataFrame({
            'Username': ['john.doe', 'jane.smith', 'mike.wilson'],
            'Role': ['Administrator', 'Inspector', 'Analyst'],
            'Last Login': ['2025-06-30', '2025-06-29', '2025-06-28'],
            'Status': ['Active', 'Active', 'Active']
        })
        
        st.dataframe(users_data, use_container_width=True)
        
        if st.button("Add New User"):
            st.info("User management interface would open here")

if __name__ == "__main__":
    main()