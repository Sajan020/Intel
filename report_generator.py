from datetime import datetime
from typing import Dict, List, Any
import json

class ReportGenerator:
    """
    Generate comprehensive reports for corrosion detection results.
    """
    
    def __init__(self):
        self.report_template = {
            'header': self._get_header_template(),
            'summary': self._get_summary_template(),
            'detailed': self._get_detailed_template(),
            'recommendations': self._get_recommendations_template(),
            'footer': self._get_footer_template()
        }
    
    def generate_report(self, data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive corrosion detection report.
        
        Args:
            data: Dictionary containing report data
            
        Returns:
            Formatted report string
        """
        report_sections = []
        
        # Header
        report_sections.append(self._generate_header(data))
        
        # Executive Summary
        report_sections.append(self._generate_summary(data))
        
        # Detailed Findings
        if data.get('detections'):
            report_sections.append(self._generate_detailed_findings(data))
        else:
            report_sections.append(self._generate_clean_inspection(data))
        
        # Recommendations
        report_sections.append(self._generate_recommendations(data))
        
        # Technical Details
        if data.get('report_type') == 'Technical':
            report_sections.append(self._generate_technical_details(data))
        
        # Footer
        report_sections.append(self._generate_footer(data))
        
        return '\n\n'.join(report_sections)
    
    def _get_header_template(self) -> str:
        return """
PIPELINE CORROSION DETECTION REPORT
{'='*50}
AI-Powered Inspection System
"""
    
    def _get_summary_template(self) -> str:
        return """
EXECUTIVE SUMMARY
{'-'*20}
"""
    
    def _get_detailed_template(self) -> str:
        return """
DETAILED FINDINGS
{'-'*20}
"""
    
    def _get_recommendations_template(self) -> str:
        return """
RECOMMENDATIONS & NEXT STEPS
{'-'*30}
"""
    
    def _get_footer_template(self) -> str:
        return """
REPORT VALIDATION
{'-'*20}
"""
    
    def _generate_header(self, data: Dict[str, Any]) -> str:
        """Generate report header section."""
        return f"""PIPELINE CORROSION DETECTION REPORT
{'='*50}
AI-Powered Inspection System

INSPECTION DETAILS:
- Inspector: {data.get('inspector_name', 'Unknown')}
- Location: {data.get('location', 'Unknown')}
- Date: {data.get('inspection_date', 'Unknown')}
- Pipeline Type: {data.get('pipeline_type', 'Unknown')}
- Image File: {data.get('image_name', 'Unknown')}
- Report Type: {data.get('report_type', 'Standard')}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        total_detections = data.get('total_detections', 0)
        avg_confidence = data.get('avg_confidence', 0)
        severity_counts = data.get('severity_counts', {})
        
        # Determine overall assessment
        if total_detections == 0:
            overall_status = "GOOD"
            status_description = "No corrosion detected in the inspected area."
        elif severity_counts.get('Critical', 0) > 0:
            overall_status = "CRITICAL"
            status_description = "Critical corrosion detected requiring immediate attention."
        elif severity_counts.get('High', 0) > 0:
            overall_status = "HIGH RISK"
            status_description = "High severity corrosion detected requiring prompt maintenance."
        elif severity_counts.get('Medium', 0) > 0:
            overall_status = "MODERATE RISK"
            status_description = "Medium severity corrosion detected requiring scheduled maintenance."
        else:
            overall_status = "LOW RISK"
            status_description = "Low severity corrosion detected for monitoring."
        
        summary = f"""EXECUTIVE SUMMARY
{'-'*20}

OVERALL STATUS: {overall_status}
{status_description}

DETECTION STATISTICS:
- Total Corrosion Areas: {total_detections}
- Average Confidence: {avg_confidence:.1%}

SEVERITY BREAKDOWN:"""
        
        if severity_counts:
            for severity in ['Critical', 'High', 'Medium', 'Low']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    summary += f"\n- {severity}: {count} area(s)"
        else:
            summary += "\n- No corrosion detected"
        
        return summary
    
    def _generate_detailed_findings(self, data: Dict[str, Any]) -> str:
        """Generate detailed findings section."""
        detections = data.get('detections', [])
        
        if not detections:
            return self._generate_clean_inspection(data)
        
        detailed = f"""DETAILED FINDINGS
{'-'*20}

Total corrosion areas identified: {len(detections)}

INDIVIDUAL CORROSION AREAS:"""
        
        for i, detection in enumerate(detections, 1):
            detailed += f"""

{i}. CORROSION AREA C{detection['id']:03d}
   Location: X={detection['bbox'][0]}, Y={detection['bbox'][1]}
   Dimensions: {detection['bbox'][2]} x {detection['bbox'][3]} pixels
   Area: {detection['area']} square pixels
   Confidence: {detection['confidence']:.1%}
   Severity: {detection['severity']}
   Risk Assessment: {detection['risk_assessment']}
   Shape Characteristics:
   - Circularity: {detection.get('circularity', 'N/A')}
   - Aspect Ratio: {detection.get('aspect_ratio', 'N/A')}
   - Extent: {detection.get('extent', 'N/A')}"""
        
        return detailed
    
    def _generate_clean_inspection(self, data: Dict[str, Any]) -> str:
        """Generate section for clean inspection (no corrosion found)."""
        return f"""INSPECTION RESULTS
{'-'*20}

✓ NO CORROSION DETECTED

The AI-powered analysis of the pipeline image did not identify any areas 
of concern that match corrosion patterns. The pipeline surface appears 
to be in good condition in the inspected area.

ANALYSIS PARAMETERS:
- Detection sensitivity: Standard
- Minimum area threshold: Applied
- Color analysis: Completed
- Texture analysis: Completed
- Edge detection: Completed

This clean inspection result indicates the pipeline coating and surface 
integrity appear satisfactory in the examined section."""
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        detections = data.get('detections', [])
        severity_counts = data.get('severity_counts', {})
        
        recommendations = f"""RECOMMENDATIONS & NEXT STEPS
{'-'*30}"""
        
        if not detections:
            recommendations += """

MAINTENANCE RECOMMENDATIONS:
✓ Continue routine inspection schedule
✓ Monitor coating condition during next scheduled inspection
✓ Document this clean inspection in maintenance records

PREVENTIVE MEASURES:
- Maintain current corrosion protection systems
- Continue environmental monitoring
- Ensure proper coating maintenance schedule"""
        else:
            # Priority actions based on severity
            if severity_counts.get('Critical', 0) > 0:
                recommendations += f"""

IMMEDIATE ACTIONS REQUIRED:
⚠️ CRITICAL corrosion areas detected - Immediate inspection and repair needed
- Isolate affected pipeline sections if possible
- Deploy field inspection team within 24 hours
- Prepare emergency repair materials
- Consider temporary operational restrictions"""
            
            if severity_counts.get('High', 0) > 0:
                recommendations += f"""

HIGH PRIORITY ACTIONS (Within 30 days):
- Schedule detailed manual inspection of identified areas
- Prepare maintenance materials and equipment
- Plan pipeline downtime for repairs
- Assess coating failure patterns"""
            
            if severity_counts.get('Medium', 0) > 0:
                recommendations += f"""

MEDIUM PRIORITY ACTIONS (Within 90 days):
- Include in next scheduled maintenance window
- Monitor progression with follow-up imaging
- Plan preventive coating repairs
- Review environmental factors contributing to corrosion"""
            
            if severity_counts.get('Low', 0) > 0:
                recommendations += f"""

MONITORING ACTIONS:
- Document locations for trending analysis
- Include in routine inspection checklist
- Monitor environmental conditions
- Consider preventive treatments"""
            
            recommendations += f"""

FOLLOW-UP ACTIONS:
- Validate AI detections with manual inspection
- Document all findings in maintenance management system
- Update inspection frequency based on findings
- Review corrosion protection system effectiveness
- Consider additional protective measures if patterns emerge"""
        
        return recommendations
    
    def _generate_technical_details(self, data: Dict[str, Any]) -> str:
        """Generate technical details section for technical reports."""
        return f"""TECHNICAL ANALYSIS DETAILS
{'-'*30}

DETECTION METHODOLOGY:
- Computer Vision Algorithm: Multi-method corrosion detection
- Color Space Analysis: HSV color space for rust detection
- Texture Analysis: Local standard deviation patterns
- Edge Detection: Canny edge detection with morphological operations
- Confidence Scoring: Weighted combination of color, texture, and shape features

ANALYSIS PARAMETERS:
- Pipeline Type: {data.get('pipeline_type', 'Unknown')}
- Detection Sensitivity: Configurable threshold-based
- Minimum Area Filter: Applied to reduce false positives
- Color Range Optimization: Pipeline-type specific tuning

ALGORITHM CONFIDENCE:
- This system provides assistance in corrosion detection
- Manual verification recommended for all detections
- False positive rate varies with image quality and lighting conditions
- Best results achieved with high-resolution, well-lit images

LIMITATIONS:
- Lighting conditions affect detection accuracy
- Surface coatings may mask early-stage corrosion
- System trained on common corrosion patterns
- Manual inspection required for verification"""
    
    def _generate_footer(self, data: Dict[str, Any]) -> str:
        """Generate report footer section."""
        return f"""REPORT VALIDATION
{'-'*20}

This report was generated by an AI-powered corrosion detection system.
All findings should be validated through manual inspection by qualified personnel.

QUALITY ASSURANCE:
- Automated detection algorithms applied
- Multi-method validation used
- Confidence scoring provided for all detections
- Professional review recommended

DISCLAIMERS:
- This analysis provides assistance in identifying potential corrosion areas
- Manual verification is required for all findings
- Environmental factors may affect detection accuracy
- Regular system calibration and validation recommended

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Version: Pipeline Corrosion Detection v1.0
Inspector: {data.get('inspector_name', 'Unknown')}

{'='*60}
END OF REPORT"""
