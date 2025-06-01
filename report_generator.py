"""
Report Generator module for formatting AI responses into structured reports
Creates professional reports for agents, managers, and engineering teams
"""

from typing import Dict, Any, List
from datetime import datetime
import json

class ReportGenerator:
    def __init__(self):
        self.report_templates = {
            "standard": self._generate_standard_report,
            "escalation": self._generate_escalation_report,
            "summary": self._generate_summary_report,
            "engineering": self._generate_engineering_report
        }
    
    def generate_complete_report(self, 
                               ticket_data: Dict[str, Any], 
                               ai_response: Dict[str, Any],
                               privacy_report: Dict[str, Any],
                               report_type: str = "standard") -> str:
        """
        Generate complete formatted report
        """
        if report_type not in self.report_templates:
            report_type = "standard"
        
        return self.report_templates[report_type](ticket_data, ai_response, privacy_report)
    
    def _generate_standard_report(self, 
                                ticket_data: Dict[str, Any], 
                                ai_response: Dict[str, Any],
                                privacy_report: Dict[str, Any]) -> str:
        """Generate standard troubleshooting report"""
        
        report_sections = []
        
        # Header
        report_sections.append(self._create_header(ai_response.get("ticket_id", "Unknown")))
        
        # AI Suggested Troubleshooting Steps
        report_sections.append(self._create_troubleshooting_section(ai_response))
        
        # Call Script
        report_sections.append(self._create_call_script_section(ai_response))
        
        # Ticket Update
        report_sections.append(self._create_ticket_update_section(ai_response))
        
        # Escalation Analysis
        report_sections.append(self._create_escalation_section(ai_response))
        
        # Privacy Notice
        if privacy_report.get("pii_removed"):
            report_sections.append(self._create_privacy_section(privacy_report))
        
        # Footer
        report_sections.append(self._create_footer())
        
        return "\n\n".join(report_sections)
    
    def _generate_escalation_report(self, 
                                  ticket_data: Dict[str, Any], 
                                  ai_response: Dict[str, Any],
                                  privacy_report: Dict[str, Any]) -> str:
        """Generate escalation-focused report"""
        
        report_sections = []
        
        # Escalation Header
        report_sections.append("🚨 ESCALATION REPORT")
        report_sections.append("=" * 60)
        
        # Critical Info
        escalation = ai_response.get("escalation_analysis", {})
        probability = escalation.get("probability", 0)
        
        report_sections.append(f"📊 **Escalation Probability:** {probability}%")
        report_sections.append(f"⚡ **Urgency Level:** {escalation.get('urgency', 'Medium')}")
        report_sections.append(f"🎯 **Recommended Path:** {escalation.get('recommended_path', 'Tier 2')}")
        report_sections.append(f"💡 **Primary Reason:** {escalation.get('reason', 'Standard progression')}")
        
        # Quick Actions
        report_sections.append("\n🔧 **IMMEDIATE ACTIONS REQUIRED:**")
        report_sections.append("-" * 40)
        
        steps = ai_response.get("troubleshooting_steps", [])
        for i, step in enumerate(steps[:3], 1):
            report_sections.append(f"{i}. {step}")
        
        # Technical Details
        if ticket_data.get("device_details"):
            report_sections.append("\n🔧 **TECHNICAL DETAILS:**")
            report_sections.append("-" * 40)
            for key, value in ticket_data["device_details"].items():
                if value and value != "[REMOVED]":
                    report_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        # Contact Script (abbreviated)
        report_sections.append("\n📞 **ESCALATION CONTACT SCRIPT:**")
        report_sections.append("-" * 40)
        script = ai_response.get("call_script", "")
        if script:
            # Take first 200 characters
            abbreviated_script = script[:200] + "..." if len(script) > 200 else script
            report_sections.append(abbreviated_script)
        
        return "\n".join(report_sections)
    
    def _generate_summary_report(self, 
                               ticket_data: Dict[str, Any], 
                               ai_response: Dict[str, Any],
                               privacy_report: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        
        report_sections = []
        
        # Executive Summary Header
        report_sections.append("📊 EXECUTIVE SUMMARY")
        report_sections.append("=" * 50)
        
        # Key Metrics
        escalation = ai_response.get("escalation_analysis", {})
        confidence = ai_response.get("confidence_score", "Medium")
        
        report_sections.append(f"**Ticket ID:** {ai_response.get('ticket_id', 'Unknown')}")
        report_sections.append(f"**Analysis Confidence:** {confidence}")
        report_sections.append(f"**Escalation Risk:** {escalation.get('probability', 50)}%")
        report_sections.append(f"**Recommended Action:** {escalation.get('recommended_path', 'Continue troubleshooting')}")
        
        # Issue Summary
        if ticket_data.get("issue_description"):
            report_sections.append(f"\n**Issue Summary:**")
            issue_desc = ticket_data["issue_description"]
            summary = issue_desc[:150] + "..." if len(issue_desc) > 150 else issue_desc
            report_sections.append(summary)
        
        # Progress Status
        completed_steps = ticket_data.get("troubleshooting_completed", [])
        suggested_steps = ai_response.get("troubleshooting_steps", [])
        
        report_sections.append(f"\n**Progress Status:**")
        report_sections.append(f"• Steps Completed: {len(completed_steps)}")
        report_sections.append(f"• Next Steps Available: {len(suggested_steps)}")
        
        # Privacy Compliance
        if privacy_report.get("pii_removed"):
            report_sections.append(f"• Privacy Compliance: ✅ PII Anonymized")
        else:
            report_sections.append(f"• Privacy Compliance: ✅ No PII Detected")
        
        return "\n".join(report_sections)
    
    def _generate_engineering_report(self, 
                                   ticket_data: Dict[str, Any], 
                                   ai_response: Dict[str, Any],
                                   privacy_report: Dict[str, Any]) -> str:
        """Generate technical report for engineering team"""
        
        report_sections = []
        
        # Engineering Header
        report_sections.append("⚙️ ENGINEERING ESCALATION REPORT")
        report_sections.append("=" * 60)
        
        # Technical Summary
        report_sections.append("🔧 **TECHNICAL SUMMARY**")
        report_sections.append("-" * 30)
        
        if ticket_data.get("issue_description"):
            report_sections.append(f"**Issue:** {ticket_data['issue_description']}")
        
        # Device Information
        if ticket_data.get("device_details"):
            report_sections.append("\n**Device Information:**")
            for key, value in ticket_data["device_details"].items():
                if value and value not in ["[REMOVED]", "[EMAIL_REMOVED]", "[PHONE_REMOVED]"]:
                    report_sections.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        # Troubleshooting History
        completed_steps = ticket_data.get("troubleshooting_completed", [])
        if completed_steps:
            report_sections.append("\n**Completed Troubleshooting:**")
            for step in completed_steps:
                report_sections.append(f"✅ {step}")
        
        # Recommended Next Steps
        suggested_steps = ai_response.get("troubleshooting_steps", [])
        if suggested_steps:
            report_sections.append("\n**AI-Recommended Next Steps:**")
            for i, step in enumerate(suggested_steps, 1):
                report_sections.append(f"{i}. {step}")
        
        # Escalation Analysis
        escalation = ai_response.get("escalation_analysis", {})
        report_sections.append(f"\n**Escalation Assessment:**")
        report_sections.append(f"• Probability: {escalation.get('probability', 50)}%")
        report_sections.append(f"• Urgency: {escalation.get('urgency', 'Medium')}")
        report_sections.append(f"• Reason: {escalation.get('reason', 'Standard assessment')}")
        
        # System Information
        report_sections.append(f"\n**System Information:**")
        report_sections.append(f"• Analysis Timestamp: {ai_response.get('analysis_timestamp', 'Unknown')}")
        report_sections.append(f"• Confidence Score: {ai_response.get('confidence_score', 'Medium')}")
        
        return "\n".join(report_sections)
    
    def _create_header(self, ticket_id: str) -> str:
        """Create report header"""
        return f"""==========================================================
📤 AI-GENERATED OUTPUT: TROUBLESHOOTING & ESCALATION  
==========================================================
🎫 Ticket ID: {ticket_id}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _create_troubleshooting_section(self, ai_response: Dict[str, Any]) -> str:
        """Create troubleshooting steps section"""
        steps = ai_response.get("troubleshooting_steps", [])
        
        section = ["🔍 AI-Suggested Next Troubleshooting Steps", "-" * 58]
        
        if steps:
            for step in steps:
                section.append(f"✔️ {step}")
        else:
            section.append("No specific steps generated")
        
        return "\n".join(section)
    
    def _create_call_script_section(self, ai_response: Dict[str, Any]) -> str:
        """Create call script section"""
        script = ai_response.get("call_script", "")
        
        section = ["📞 AI-Generated Call Script for Tier 2 Agent", "-" * 58]
        
        if script:
            # Format the script with proper line breaks
            formatted_script = script.replace('. ', '.\n').replace('? ', '?\n')
            section.append(f'_"{formatted_script}"_')
        else:
            section.append("No call script generated")
        
        return "\n".join(section)
    
    def _create_ticket_update_section(self, ai_response: Dict[str, Any]) -> str:
        """Create ticket update section"""
        update = ai_response.get("ticket_update", "")
        
        section = ["🔁 AI-Generated Ticket Update for Zendesk", "-" * 58]
        
        if update:
            section.append(update)
        else:
            section.append("No ticket update generated")
        
        return "\n".join(section)
    
    def _create_escalation_section(self, ai_response: Dict[str, Any]) -> str:
        """Create escalation prediction section"""
        escalation = ai_response.get("escalation_analysis", {})
        
        section = ["📊 AI Escalation Prediction Output", "-" * 58]
        
        ticket_id = ai_response.get("ticket_id", "Unknown")
        probability = escalation.get("probability", 50)
        urgency = escalation.get("urgency", "Medium")
        path = escalation.get("recommended_path", "Tier 2 Support")
        reason = escalation.get("reason", "Standard assessment")
        
        section.extend([
            f"🔹 **Ticket ID:** {ticket_id}",
            f"🔹 **Issue Type:** Network connectivity failure",
            f"🔹 **Escalation Prediction:** {probability}% chance of requiring {path}",
            f"🔹 **Urgency Level:** {urgency}",
            f"🔹 **Primary Reason:** {reason}"
        ])
        
        return "\n".join(section)
    
    def _create_privacy_section(self, privacy_report: Dict[str, Any]) -> str:
        """Create privacy notice section"""
        section = ["🔐 DATA PRIVACY NOTICE", "-" * 58]
        
        section.extend([
            "⚠️ **Sensitive customer data has been anonymized to prevent data leakage.**",
            "✔️ Contact details anonymized",
            "✔️ Personal information removed",
            "✔️ Device identifiers preserved for technical support",
            "✔️ No personally identifiable information retained"
        ])
        
        if privacy_report.get("summary"):
            pii_summary = []
            for pii_type, count in privacy_report["summary"].items():
                if count > 0:
                    pii_summary.append(f"{pii_type}: {count} items")
            
            if pii_summary:
                section.append(f"📊 **Items Processed:** {', '.join(pii_summary)}")
        
        return "\n".join(section)
    
    def _create_footer(self) -> str:
        """Create report footer"""
        return """==========================================================  
**END OF REPORT**  
=========================================================="""
    
    def generate_downloadable_report(self, 
                                   ticket_data: Dict[str, Any], 
                                   ai_response: Dict[str, Any],
                                   privacy_report: Dict[str, Any],
                                   format_type: str = "txt") -> bytes:
        """
        Generate downloadable report in specified format
        """
        report_content = self.generate_complete_report(ticket_data, ai_response, privacy_report)
        
        if format_type.lower() == "json":
            # Create JSON version
            json_data = {
                "ticket_data": ticket_data,
                "ai_response": ai_response,
                "privacy_report": privacy_report,
                "generated_report": report_content,
                "export_timestamp": datetime.now().isoformat()
            }
            return json.dumps(json_data, indent=2).encode('utf-8')
        
        else:  # Default to text format
            return report_content.encode('utf-8')
    
    def get_report_filename(self, ticket_id: str, format_type: str = "txt") -> str:
        """Generate appropriate filename for report download"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"support_report_{ticket_id}_{timestamp}.{format_type}"
    
    def create_batch_summary(self, reports: List[Dict[str, Any]]) -> str:
        """Create summary report for multiple tickets"""
        if not reports:
            return "No reports to summarize"
        
        summary_sections = []
        
        # Header
        summary_sections.append("📊 BATCH PROCESSING SUMMARY")
        summary_sections.append("=" * 50)
        summary_sections.append(f"Total Tickets Processed: {len(reports)}")
        summary_sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Statistics
        high_escalation = sum(1 for r in reports 
                            if r.get("ai_response", {}).get("escalation_analysis", {}).get("probability", 0) > 70)
        
        pii_processed = sum(1 for r in reports 
                          if r.get("privacy_report", {}).get("pii_removed", False))
        
        summary_sections.extend([
            f"\n📈 **Statistics:**",
            f"• High Escalation Risk: {high_escalation} tickets ({(high_escalation/len(reports)*100):.1f}%)",
            f"• PII Processed: {pii_processed} tickets ({(pii_processed/len(reports)*100):.1f}%)",
        ])
        
        # Top Issues (if available)
        summary_sections.append(f"\n🔍 **Processed Tickets:**")
        for i, report in enumerate(reports[:10], 1):  # Show first 10
            ticket_id = report.get("ai_response", {}).get("ticket_id", f"Report {i}")
            escalation_prob = report.get("ai_response", {}).get("escalation_analysis", {}).get("probability", 0)
            summary_sections.append(f"{i}. {ticket_id} - Escalation: {escalation_prob}%")
        
        if len(reports) > 10:
            summary_sections.append(f"... and {len(reports) - 10} more tickets")
        
        return "\n".join(summary_sections)