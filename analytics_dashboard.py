import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from database import DatabaseManager
import numpy as np

class AnalyticsDashboard:
    """Advanced analytics dashboard for pipeline corrosion management"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def render_executive_dashboard(self):
        """Render executive-level analytics dashboard"""
        st.header("📊 Executive Dashboard")
        st.markdown("### Pipeline Corrosion Management Overview")
        
        # KPI Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Total inspections this month
            inspections = self.db_manager.get_inspection_history()
            monthly_inspections = len([i for i in inspections 
                                     if i['inspection_date'].month == datetime.now().month])
            st.metric("Monthly Inspections", monthly_inspections)
        
        with col2:
            # Critical alerts
            alerts = self.db_manager.get_pending_alerts()
            critical_alerts = len([a for a in alerts if a['severity'] == 'Critical'])
            st.metric("Critical Alerts", critical_alerts, delta=None if critical_alerts == 0 else f"+{critical_alerts}")
        
        with col3:
            # Average detection confidence
            if inspections:
                avg_confidence = np.mean([i['avg_confidence'] for i in inspections if i['avg_confidence']])
                st.metric("Avg Detection Confidence", f"{avg_confidence:.1%}")
            else:
                st.metric("Avg Detection Confidence", "N/A")
        
        with col4:
            # Pipeline segments monitored
            st.metric("Pipeline Segments", "0", help="Add pipeline segments to track")
        
        # Charts Row
        col_left, col_right = st.columns(2)
        
        with col_left:
            self._render_corrosion_trends_chart()
        
        with col_right:
            self._render_severity_distribution()
        
        # Map and Alerts
        st.markdown("---")
        
        col_map, col_alerts = st.columns([2, 1])
        
        with col_map:
            self._render_pipeline_map()
        
        with col_alerts:
            self._render_alert_panel()
    
    def _render_corrosion_trends_chart(self):
        """Render corrosion trends over time"""
        st.subheader("Corrosion Detection Trends")
        
        # Sample data for demonstration
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        detection_counts = np.random.poisson(15, len(dates))
        critical_counts = np.random.poisson(2, len(dates))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=detection_counts,
            mode='lines+markers',
            name='Total Detections',
            line=dict(color='#1f77b4')
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=critical_counts,
            mode='lines+markers',
            name='Critical Detections',
            line=dict(color='#d62728')
        ))
        
        fig.update_layout(
            title="Corrosion Detection Trends",
            xaxis_title="Date",
            yaxis_title="Number of Detections",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_severity_distribution(self):
        """Render severity level distribution"""
        st.subheader("Severity Distribution")
        
        # Sample data
        severity_data = {
            'Severity': ['Critical', 'High', 'Medium', 'Low'],
            'Count': [5, 12, 28, 45],
            'Color': ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c']
        }
        
        fig = px.pie(
            values=severity_data['Count'],
            names=severity_data['Severity'],
            color=severity_data['Severity'],
            color_discrete_map={
                'Critical': '#d62728',
                'High': '#ff7f0e',
                'Medium': '#ffbb78',
                'Low': '#2ca02c'
            }
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title="Current Severity Distribution")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_pipeline_map(self):
        """Render interactive pipeline map"""
        st.subheader("Pipeline Network Map")
        
        # Create sample pipeline map
        m = folium.Map(location=[29.7604, -95.3698], zoom_start=10)  # Houston area
        
        # Sample pipeline segments with corrosion data
        pipeline_segments = [
            {"lat": 29.7604, "lon": -95.3698, "name": "Segment A", "status": "Critical", "detections": 8},
            {"lat": 29.7804, "lon": -95.3498, "name": "Segment B", "status": "Good", "detections": 0},
            {"lat": 29.7404, "lon": -95.3898, "name": "Segment C", "status": "Medium", "detections": 3},
            {"lat": 29.7704, "lon": -95.3598, "name": "Segment D", "status": "High", "detections": 5},
        ]
        
        # Color mapping for status
        color_map = {
            "Critical": "red",
            "High": "orange", 
            "Medium": "yellow",
            "Good": "green"
        }
        
        for segment in pipeline_segments:
            folium.CircleMarker(
                location=[segment["lat"], segment["lon"]],
                radius=10,
                popup=folium.Popup(
                    f"<b>{segment['name']}</b><br>"
                    f"Status: {segment['status']}<br>"
                    f"Detections: {segment['detections']}",
                    max_width=200
                ),
                color=color_map[segment["status"]],
                fill=True,
                fillColor=color_map[segment["status"]],
                fillOpacity=0.7
            ).add_to(m)
        
        # Add pipeline lines
        pipeline_coords = [[seg["lat"], seg["lon"]] for seg in pipeline_segments]
        folium.PolyLine(
            locations=pipeline_coords,
            color="blue",
            weight=3,
            opacity=0.8,
            popup="Main Pipeline"
        ).add_to(m)
        
        map_data = st_folium(m, width=700, height=400)
    
    def _render_alert_panel(self):
        """Render system alerts panel"""
        st.subheader("🚨 System Alerts")
        
        # Sample alerts
        alerts = [
            {"type": "Critical Corrosion", "message": "Segment A: 8 critical detections", "time": "2 hours ago"},
            {"type": "Maintenance Due", "message": "Segment C: Inspection overdue", "time": "1 day ago"},
            {"type": "Threshold Exceeded", "message": "Segment D: High corrosion rate", "time": "3 days ago"},
        ]
        
        for alert in alerts:
            with st.container():
                if alert["type"] == "Critical Corrosion":
                    st.error(f"🔴 **{alert['type']}**")
                elif alert["type"] == "Maintenance Due":
                    st.warning(f"🟡 **{alert['type']}**")
                else:
                    st.info(f"🔵 **{alert['type']}**")
                
                st.write(f"{alert['message']}")
                st.caption(f"*{alert['time']}*")
                st.markdown("---")
    
    def render_technical_dashboard(self):
        """Render technical analysis dashboard"""
        st.header("🔬 Technical Analysis Dashboard")
        
        # Detection Algorithm Performance
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_algorithm_performance()
        
        with col2:
            self._render_confidence_distribution()
        
        # Detailed Analysis
        st.markdown("---")
        self._render_detection_characteristics()
        
        # Historical Analysis
        st.markdown("---")
        self._render_historical_analysis()
    
    def _render_algorithm_performance(self):
        """Render algorithm performance metrics"""
        st.subheader("Detection Algorithm Performance")
        
        methods = ['Color Analysis', 'Texture Analysis', 'Edge Detection', 'Combined']
        accuracy = [85, 78, 72, 92]
        precision = [82, 80, 68, 89]
        recall = [88, 76, 75, 94]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(name='Accuracy', x=methods, y=accuracy, marker_color='#1f77b4'))
        fig.add_trace(go.Bar(name='Precision', x=methods, y=precision, marker_color='#ff7f0e'))
        fig.add_trace(go.Bar(name='Recall', x=methods, y=recall, marker_color='#2ca02c'))
        
        fig.update_layout(
            title="Algorithm Performance Metrics (%)",
            xaxis_title="Detection Method",
            yaxis_title="Performance (%)",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_confidence_distribution(self):
        """Render confidence score distribution"""
        st.subheader("Confidence Score Distribution")
        
        # Sample confidence data
        confidence_scores = np.random.beta(2, 1, 1000)  # Beta distribution for realistic confidence scores
        
        fig = px.histogram(
            x=confidence_scores,
            nbins=20,
            title="Detection Confidence Distribution",
            labels={'x': 'Confidence Score', 'y': 'Frequency'}
        )
        
        fig.update_layout(
            xaxis=dict(tickformat='.1%'),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detection_characteristics(self):
        """Render detection characteristics analysis"""
        st.subheader("Detection Characteristics Analysis")
        
        # Sample data for detection characteristics
        detection_data = {
            'Area (px²)': np.random.lognormal(7, 1, 100),
            'Confidence': np.random.beta(2, 1, 100),
            'Severity': np.random.choice(['Low', 'Medium', 'High', 'Critical'], 100, p=[0.4, 0.35, 0.2, 0.05])
        }
        
        df = pd.DataFrame(detection_data)
        
        # Scatter plot of area vs confidence, colored by severity
        fig = px.scatter(
            df,
            x='Area (px²)',
            y='Confidence',
            color='Severity',
            color_discrete_map={
                'Low': '#2ca02c',
                'Medium': '#ffbb78',
                'High': '#ff7f0e',
                'Critical': '#d62728'
            },
            title="Detection Area vs Confidence by Severity"
        )
        
        fig.update_layout(
            xaxis_type="log",
            yaxis=dict(tickformat='.1%')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_historical_analysis(self):
        """Render historical trend analysis"""
        st.subheader("Historical Trend Analysis")
        
        # Sample historical data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='W')
        
        # Simulate corrosion progression over time
        np.random.seed(42)
        base_trend = np.linspace(10, 25, len(dates))
        seasonal_pattern = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 52)
        noise = np.random.normal(0, 2, len(dates))
        corrosion_rate = base_trend + seasonal_pattern + noise
        
        df = pd.DataFrame({
            'Date': dates,
            'Corrosion_Rate': corrosion_rate,
            'Detection_Count': np.random.poisson(corrosion_rate/2, len(dates))
        })
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Corrosion_Rate'], name="Corrosion Rate"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Detection_Count'], name="Detection Count", line=dict(color='red')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Corrosion Rate (mm/year)", secondary_y=False)
        fig.update_yaxes(title_text="Detection Count", secondary_y=True)
        
        fig.update_layout(title="Corrosion Rate vs Detection Count Over Time")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_maintenance_dashboard(self):
        """Render maintenance planning dashboard"""
        st.header("🔧 Maintenance Planning Dashboard")
        
        # Maintenance Priority Matrix
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_priority_matrix()
        
        with col2:
            self._render_maintenance_schedule()
        
        # Cost Analysis
        st.markdown("---")
        self._render_cost_analysis()
    
    def _render_priority_matrix(self):
        """Render maintenance priority matrix"""
        st.subheader("Maintenance Priority Matrix")
        
        # Sample data for priority matrix
        segments = ['Segment A', 'Segment B', 'Segment C', 'Segment D', 'Segment E']
        risk_scores = [95, 45, 70, 85, 30]
        urgency_scores = [90, 40, 60, 80, 25]
        colors = ['Critical', 'Low', 'Medium', 'High', 'Low']
        
        fig = px.scatter(
            x=risk_scores,
            y=urgency_scores,
            text=segments,
            color=colors,
            color_discrete_map={
                'Critical': '#d62728',
                'High': '#ff7f0e',
                'Medium': '#ffbb78',
                'Low': '#2ca02c'
            },
            title="Risk vs Urgency Matrix"
        )
        
        fig.update_traces(textposition="middle center", marker_size=20)
        fig.update_layout(
            xaxis_title="Risk Score",
            yaxis_title="Urgency Score",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_maintenance_schedule(self):
        """Render maintenance schedule"""
        st.subheader("Maintenance Schedule")
        
        # Sample maintenance schedule
        schedule_data = {
            'Segment': ['Segment A', 'Segment D', 'Segment C', 'Segment B'],
            'Priority': ['Critical', 'High', 'Medium', 'Low'],
            'Scheduled Date': ['2025-01-15', '2025-02-01', '2025-03-15', '2025-06-01'],
            'Type': ['Emergency Repair', 'Planned Maintenance', 'Inspection', 'Routine Check'],
            'Estimated Cost': ['$50,000', '$25,000', '$5,000', '$2,000']
        }
        
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, use_container_width=True)
    
    def _render_cost_analysis(self):
        """Render maintenance cost analysis"""
        st.subheader("Maintenance Cost Analysis")
        
        # Sample cost data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        preventive_costs = [15000, 12000, 18000, 14000, 16000, 13000]
        corrective_costs = [45000, 0, 25000, 0, 35000, 20000]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Preventive Maintenance',
            x=months,
            y=preventive_costs,
            marker_color='#2ca02c'
        ))
        
        fig.add_trace(go.Bar(
            name='Corrective Maintenance',
            x=months,
            y=corrective_costs,
            marker_color='#d62728'
        ))
        
        fig.update_layout(
            title="Maintenance Costs: Preventive vs Corrective",
            xaxis_title="Month",
            yaxis_title="Cost ($)",
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost savings calculation
        total_preventive = sum(preventive_costs)
        total_corrective = sum(corrective_costs)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Preventive Costs", f"${total_preventive:,}")
        with col2:
            st.metric("Corrective Costs", f"${total_corrective:,}")
        with col3:
            potential_savings = total_corrective * 0.7  # Assume 70% of corrective costs could be prevented
            st.metric("Potential Savings", f"${potential_savings:,.0f}", 
                     help="Estimated savings from better predictive maintenance")