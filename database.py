import os
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    raise ValueError("DATABASE_URL environment variable not set")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PipelineSegment(Base):
    """Pipeline segment information"""
    __tablename__ = "pipeline_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    segment_name = Column(String, unique=True, index=True)
    pipeline_type = Column(String)  # subsea, cross-country, etc.
    material = Column(String)
    diameter = Column(Float)
    length = Column(Float)
    installation_date = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class CorrosionInspection(Base):
    """Individual corrosion inspection records"""
    __tablename__ = "corrosion_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, index=True)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    inspector_name = Column(String)
    inspection_method = Column(String)  # AI_vision, smart_pig, manual, etc.
    image_filename = Column(String)
    total_detections = Column(Integer, default=0)
    max_severity = Column(String)
    avg_confidence = Column(Float)
    report_generated = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CorrosionDetection(Base):
    """Individual corrosion detection results"""
    __tablename__ = "corrosion_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, index=True)
    detection_id = Column(String)  # e.g., C001, C002
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)
    area = Column(Float)
    confidence = Column(Float)
    severity = Column(String)
    risk_assessment = Column(String)
    shape_characteristics = Column(JSON)  # circularity, aspect_ratio, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class MaintenanceAction(Base):
    """Maintenance actions and follow-ups"""
    __tablename__ = "maintenance_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, index=True)
    action_type = Column(String)  # repair, monitor, replace, etc.
    priority = Column(String)  # immediate, high, medium, low
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    status = Column(String, default="pending")
    assigned_to = Column(String)
    cost = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemAlert(Base):
    """System alerts and notifications"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)  # critical_corrosion, maintenance_due, etc.
    severity = Column(String)
    message = Column(Text)
    segment_id = Column(Integer)
    inspection_id = Column(Integer)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database operations class
class DatabaseManager:
    """Database operations for pipeline corrosion management"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_pipeline_segment(self, segment_data: Dict[str, Any]) -> int:
        """Add new pipeline segment"""
        db = self.get_session()
        try:
            segment = PipelineSegment(**segment_data)
            db.add(segment)
            db.commit()
            db.refresh(segment)
            return segment.id
        finally:
            db.close()
    
    def add_inspection(self, inspection_data: Dict[str, Any]) -> int:
        """Add new inspection record"""
        db = self.get_session()
        try:
            inspection = CorrosionInspection(**inspection_data)
            db.add(inspection)
            db.commit()
            db.refresh(inspection)
            return inspection.id
        finally:
            db.close()
    
    def add_detections(self, inspection_id: int, detections: List[Dict[str, Any]]):
        """Add corrosion detections for an inspection"""
        db = self.get_session()
        try:
            for detection_data in detections:
                detection = CorrosionDetection(
                    inspection_id=inspection_id,
                    detection_id=f"C{detection_data['id']:03d}",
                    bbox_x=detection_data['bbox'][0],
                    bbox_y=detection_data['bbox'][1],
                    bbox_width=detection_data['bbox'][2],
                    bbox_height=detection_data['bbox'][3],
                    area=detection_data['area'],
                    confidence=detection_data['confidence'],
                    severity=detection_data['severity'],
                    risk_assessment=detection_data['risk_assessment'],
                    shape_characteristics={
                        'circularity': detection_data.get('circularity', 0),
                        'aspect_ratio': detection_data.get('aspect_ratio', 0),
                        'extent': detection_data.get('extent', 0)
                    }
                )
                db.add(detection)
            db.commit()
        finally:
            db.close()
    
    def get_inspection_history(self, segment_id: Optional[int] = None) -> List[Dict]:
        """Get inspection history"""
        db = self.get_session()
        try:
            query = db.query(CorrosionInspection)
            if segment_id:
                query = query.filter(CorrosionInspection.segment_id == segment_id)
            
            inspections = query.order_by(CorrosionInspection.inspection_date.desc()).all()
            
            result = []
            for inspection in inspections:
                result.append({
                    'id': inspection.id,
                    'segment_id': inspection.segment_id,
                    'inspection_date': inspection.inspection_date,
                    'inspector_name': inspection.inspector_name,
                    'total_detections': inspection.total_detections,
                    'max_severity': inspection.max_severity,
                    'avg_confidence': inspection.avg_confidence
                })
            
            return result
        finally:
            db.close()
    
    def get_corrosion_trends(self, segment_id: int, days: int = 365) -> Dict:
        """Get corrosion trends for a pipeline segment"""
        db = self.get_session()
        try:
            # Get inspection data
            inspections = db.query(CorrosionInspection).filter(
                CorrosionInspection.segment_id == segment_id,
                CorrosionInspection.inspection_date >= datetime.now() - timedelta(days=days)
            ).order_by(CorrosionInspection.inspection_date).all()
            
            # Get detection counts by severity over time
            trend_data = {
                'dates': [],
                'total_detections': [],
                'critical_count': [],
                'high_count': [],
                'medium_count': [],
                'low_count': []
            }
            
            for inspection in inspections:
                trend_data['dates'].append(inspection.inspection_date.strftime('%Y-%m-%d'))
                trend_data['total_detections'].append(inspection.total_detections)
                
                # Get severity breakdown for this inspection
                detections = db.query(CorrosionDetection).filter(
                    CorrosionDetection.inspection_id == inspection.id
                ).all()
                
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                for detection in detections:
                    severity_counts[detection.severity] = severity_counts.get(detection.severity, 0) + 1
                
                trend_data['critical_count'].append(severity_counts['Critical'])
                trend_data['high_count'].append(severity_counts['High'])
                trend_data['medium_count'].append(severity_counts['Medium'])
                trend_data['low_count'].append(severity_counts['Low'])
            
            return trend_data
        finally:
            db.close()
    
    def create_maintenance_alert(self, detection_id: int, alert_data: Dict[str, Any]):
        """Create maintenance alert for high-priority detections"""
        db = self.get_session()
        try:
            alert = SystemAlert(**alert_data)
            db.add(alert)
            db.commit()
        finally:
            db.close()
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get pending system alerts"""
        db = self.get_session()
        try:
            alerts = db.query(SystemAlert).filter(
                SystemAlert.acknowledged == False
            ).order_by(SystemAlert.created_at.desc()).all()
            
            result = []
            for alert in alerts:
                result.append({
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'created_at': alert.created_at
                })
            
            return result
        finally:
            db.close()

# Initialize database
db_manager = DatabaseManager()

def init_database():
    """Initialize database tables"""
    try:
        db_manager.create_tables()
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False