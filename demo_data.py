"""
Demo data provider for industrial pipeline corrosion system
This provides realistic sample data for demonstration purposes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class DemoDataProvider:
    """Provides realistic demo data for the industrial pipeline system"""
    
    def __init__(self):
        self.pipeline_segments = self._generate_pipeline_segments()
        self.inspections = self._generate_inspection_history()
        self.detections = self._generate_corrosion_detections()
        self.alerts = self._generate_system_alerts()
    
    def _generate_pipeline_segments(self) -> List[Dict]:
        """Generate sample pipeline segments"""
        segments = [
            {
                'id': 1,
                'segment_name': 'Gulf Coast Section A',
                'pipeline_type': 'subsea',
                'material': 'Carbon Steel',
                'diameter': 24,
                'length': 15.2,
                'installation_date': datetime(2010, 5, 15),
                'latitude': 29.7604,
                'longitude': -95.3698,
                'status': 'active'
            },
            {
                'id': 2,
                'segment_name': 'Cross Country Line B',
                'pipeline_type': 'cross-country',
                'material': 'Carbon Steel',
                'diameter': 30,
                'length': 25.8,
                'installation_date': datetime(2008, 3, 22),
                'latitude': 29.7804,
                'longitude': -95.3498,
                'status': 'active'
            },
            {
                'id': 3,
                'segment_name': 'Industrial Zone C',
                'pipeline_type': 'industrial',
                'material': 'Stainless Steel',
                'diameter': 18,
                'length': 8.5,
                'installation_date': datetime(2015, 9, 10),
                'latitude': 29.7404,
                'longitude': -95.3898,
                'status': 'active'
            },
            {
                'id': 4,
                'segment_name': 'Urban Section D',
                'pipeline_type': 'urban',
                'material': 'Composite',
                'diameter': 20,
                'length': 12.3,
                'installation_date': datetime(2018, 11, 5),
                'latitude': 29.7704,
                'longitude': -95.3598,
                'status': 'active'
            }
        ]
        return segments
    
    def _generate_inspection_history(self) -> List[Dict]:
        """Generate sample inspection history"""
        inspections = []
        
        # Generate inspections for the last 2 years
        start_date = datetime.now() - timedelta(days=730)
        
        for i in range(50):  # 50 inspections over 2 years
            inspection_date = start_date + timedelta(days=random.randint(0, 730))
            segment_id = random.choice([1, 2, 3, 4])
            
            # Generate realistic detection counts based on segment type
            segment = next(s for s in self.pipeline_segments if s['id'] == segment_id)
            if segment['pipeline_type'] == 'subsea':
                total_detections = random.randint(3, 15)
            elif segment['pipeline_type'] == 'industrial':
                total_detections = random.randint(1, 8)
            else:
                total_detections = random.randint(0, 6)
            
            # Determine max severity based on detection count
            if total_detections == 0:
                max_severity = None
            elif total_detections > 10:
                max_severity = random.choice(['High', 'Critical'])
            elif total_detections > 5:
                max_severity = random.choice(['Medium', 'High'])
            else:
                max_severity = random.choice(['Low', 'Medium'])
            
            avg_confidence = random.uniform(0.65, 0.95) if total_detections > 0 else 0
            
            inspection = {
                'id': i + 1,
                'segment_id': segment_id,
                'inspection_date': inspection_date,
                'inspector_name': random.choice(['John Smith', 'Sarah Johnson', 'Mike Wilson', 'Lisa Chen']),
                'inspection_method': random.choice(['AI Vision', 'Smart Pig', 'Manual', 'Combined']),
                'total_detections': total_detections,
                'max_severity': max_severity,
                'avg_confidence': avg_confidence
            }
            inspections.append(inspection)
        
        return sorted(inspections, key=lambda x: x['inspection_date'], reverse=True)
    
    def _generate_corrosion_detections(self) -> List[Dict]:
        """Generate sample corrosion detections"""
        detections = []
        detection_id = 1
        
        for inspection in self.inspections:
            if inspection['total_detections'] > 0:
                for i in range(inspection['total_detections']):
                    severity_weights = {
                        'Low': 0.5,
                        'Medium': 0.3,
                        'High': 0.15,
                        'Critical': 0.05
                    }
                    
                    severity = random.choices(
                        list(severity_weights.keys()),
                        weights=list(severity_weights.values())
                    )[0]
                    
                    # Adjust confidence based on severity
                    if severity == 'Critical':
                        confidence = random.uniform(0.85, 0.98)
                        area = random.randint(2000, 8000)
                    elif severity == 'High':
                        confidence = random.uniform(0.75, 0.90)
                        area = random.randint(1000, 3000)
                    elif severity == 'Medium':
                        confidence = random.uniform(0.60, 0.80)
                        area = random.randint(500, 1500)
                    else:
                        confidence = random.uniform(0.50, 0.70)
                        area = random.randint(200, 800)
                    
                    detection = {
                        'id': detection_id,
                        'inspection_id': inspection['id'],
                        'detection_id': f'C{detection_id:03d}',
                        'bbox': [
                            random.randint(50, 800),  # x
                            random.randint(50, 600),  # y
                            random.randint(50, 200),  # width
                            random.randint(50, 200)   # height
                        ],
                        'area': area,
                        'confidence': confidence,
                        'severity': severity,
                        'risk_assessment': self._get_risk_assessment(severity),
                        'shape_characteristics': {
                            'circularity': random.uniform(0.3, 0.8),
                            'aspect_ratio': random.uniform(1.0, 3.0),
                            'extent': random.uniform(0.4, 0.9)
                        }
                    }
                    detections.append(detection)
                    detection_id += 1
        
        return detections
    
    def _get_risk_assessment(self, severity: str) -> str:
        """Get risk assessment based on severity"""
        risk_map = {
            'Critical': 'Immediate action required',
            'High': 'Schedule maintenance within 30 days',
            'Medium': 'Monitor and schedule maintenance within 90 days',
            'Low': 'Monitor during next routine inspection'
        }
        return risk_map.get(severity, 'Monitor during next routine inspection')
    
    def _generate_system_alerts(self) -> List[Dict]:
        """Generate sample system alerts"""
        alerts = []
        
        # Generate recent alerts
        for i in range(10):
            alert_date = datetime.now() - timedelta(hours=random.randint(1, 168))  # Last week
            
            alert_types = [
                'Critical Corrosion Detected',
                'Maintenance Due',
                'Threshold Exceeded',
                'System Health Check',
                'Inspection Overdue'
            ]
            
            alert_type = random.choice(alert_types)
            
            if 'Critical' in alert_type:
                severity = 'Critical'
                message = f"Critical corrosion detected in Segment {random.choice(['A', 'B', 'C', 'D'])}"
            elif 'Maintenance' in alert_type or 'Overdue' in alert_type:
                severity = 'High'
                message = f"Maintenance action required for Segment {random.choice(['A', 'B', 'C', 'D'])}"
            else:
                severity = random.choice(['Medium', 'Low'])
                message = f"System monitoring alert for Segment {random.choice(['A', 'B', 'C', 'D'])}"
            
            alert = {
                'id': i + 1,
                'alert_type': alert_type,
                'severity': severity,
                'message': message,
                'created_at': alert_date,
                'acknowledged': random.choice([True, False])
            }
            alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x['created_at'], reverse=True)
    
    def get_inspection_history(self, segment_id=None) -> List[Dict]:
        """Get inspection history"""
        if segment_id:
            return [i for i in self.inspections if i['segment_id'] == segment_id]
        return self.inspections
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get pending alerts"""
        return [a for a in self.alerts if not a['acknowledged']]
    
    def get_corrosion_trends(self, segment_id: int, days: int = 365) -> Dict:
        """Get corrosion trends for analytics"""
        # Filter inspections for the segment and time period
        cutoff_date = datetime.now() - timedelta(days=days)
        segment_inspections = [
            i for i in self.inspections 
            if i['segment_id'] == segment_id and i['inspection_date'] >= cutoff_date
        ]
        
        trend_data = {
            'dates': [],
            'total_detections': [],
            'critical_count': [],
            'high_count': [],
            'medium_count': [],
            'low_count': []
        }
        
        for inspection in segment_inspections:
            trend_data['dates'].append(inspection['inspection_date'].strftime('%Y-%m-%d'))
            trend_data['total_detections'].append(inspection['total_detections'])
            
            # Get severity breakdown for this inspection
            inspection_detections = [
                d for d in self.detections 
                if d['inspection_id'] == inspection['id']
            ]
            
            severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
            for detection in inspection_detections:
                severity_counts[detection['severity']] += 1
            
            trend_data['critical_count'].append(severity_counts['Critical'])
            trend_data['high_count'].append(severity_counts['High'])
            trend_data['medium_count'].append(severity_counts['Medium'])
            trend_data['low_count'].append(severity_counts['Low'])
        
        return trend_data
    
    def get_monthly_inspection_count(self) -> int:
        """Get current month inspection count"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        return len([
            i for i in self.inspections 
            if i['inspection_date'].month == current_month and i['inspection_date'].year == current_year
        ])
    
    def get_pipeline_segments(self) -> List[Dict]:
        """Get all pipeline segments"""
        return self.pipeline_segments
    
    def get_detection_summary(self) -> Dict:
        """Get overall detection summary"""
        total_detections = len(self.detections)
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        
        for detection in self.detections:
            severity_counts[detection['severity']] += 1
        
        avg_confidence = np.mean([d['confidence'] for d in self.detections]) if self.detections else 0
        
        return {
            'total_detections': total_detections,
            'severity_counts': severity_counts,
            'avg_confidence': avg_confidence,
            'last_inspection': max(self.inspections, key=lambda x: x['inspection_date'])['inspection_date'] if self.inspections else None
        }

# Global instance for use across the application
demo_data = DemoDataProvider()