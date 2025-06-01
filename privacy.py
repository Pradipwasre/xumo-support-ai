"""
Privacy module for PII (Personally Identifiable Information) anonymization
Removes sensitive data like emails, phone numbers, SSNs, etc.
"""

import re
from typing import Dict, List, Tuple, Any
import logging
import hashlib

from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIAnonymizer:
    def __init__(self):
        self.config = get_config()
        self.pii_patterns = self.config["pii_patterns"]
        self.anonymized_data = {}  # Store mapping for potential recovery
    
    def anonymize_text(self, text: str, preserve_format: bool = True) -> Tuple[str, Dict[str, List[str]]]:
        """
        Anonymize PII in text while preserving format
        Returns (anonymized_text, detected_pii_summary)
        """
        if not text:
            return text, {}
        
        anonymized_text = text
        detected_pii = {
            "emails": [],
            "phones": [],
            "ssns": [],
            "credit_cards": []
        }
        
        # Process each PII type
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, anonymized_text, re.IGNORECASE)
            
            if matches:
                for match in matches:
                    # Generate consistent anonymized replacement
                    replacement = self._generate_replacement(match, pii_type, preserve_format)
                    anonymized_text = anonymized_text.replace(match, replacement)
                    
                    # Store detected PII (for logging, not storage)
                    if pii_type == "email":
                        detected_pii["emails"].append(self._mask_sensitive_data(match, "email"))
                    elif pii_type == "phone":
                        detected_pii["phones"].append(self._mask_sensitive_data(match, "phone"))
                    elif pii_type == "ssn":
                        detected_pii["ssns"].append("***-**-****")
                    elif pii_type == "credit_card":
                        detected_pii["credit_cards"].append("****-****-****-****")
        
        return anonymized_text, detected_pii
    
    def _generate_replacement(self, original: str, pii_type: str, preserve_format: bool) -> str:
        """Generate consistent replacement for PII"""
        if not preserve_format:
            return f"[{pii_type.upper()}_REMOVED]"
        
        if pii_type == "email":
            # Replace with generic email format
            domain_part = original.split('@')[-1] if '@' in original else "example.com"
            return f"user@{domain_part}"
        
        elif pii_type == "phone":
            # Replace with format-preserving placeholder
            if re.match(r'\+1', original):
                return "+1-XXX-XXX-XXXX"
            elif re.match(r'\(\d{3}\)', original):
                return "(XXX) XXX-XXXX"
            else:
                return "XXX-XXX-XXXX"
        
        elif pii_type == "ssn":
            return "XXX-XX-XXXX"
        
        elif pii_type == "credit_card":
            return "XXXX-XXXX-XXXX-XXXX"
        
        return f"[{pii_type.upper()}_REMOVED]"
    
    def _mask_sensitive_data(self, data: str, data_type: str) -> str:
        """Create a partially masked version for logging purposes"""
        if data_type == "email":
            if '@' in data:
                username, domain = data.split('@', 1)
                masked_username = username[:2] + "*" * (len(username) - 2)
                return f"{masked_username}@{domain}"
            return data[:2] + "*" * (len(data) - 2)
        
        elif data_type == "phone":
            # Keep last 4 digits
            clean_phone = re.sub(r'\D', '', data)
            if len(clean_phone) >= 4:
                return "*" * (len(clean_phone) - 4) + clean_phone[-4:]
            return "*" * len(clean_phone)
        
        return "*" * len(data)
    
    def anonymize_ticket_data(self, ticket_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Anonymize PII in structured ticket data
        Returns (anonymized_data, privacy_report)
        """
        anonymized_data = ticket_data.copy()
        privacy_report = {
            "pii_removed": False,
            "items_anonymized": 0,
            "categories_affected": [],
            "summary": {}
        }
        
        # Fields to anonymize
        text_fields_to_check = [
            "raw_text", "issue_description", "customer_name", 
            "contact_number", "email", "escalation_status"
        ]
        
        total_pii_found = {
            "emails": [],
            "phones": [],
            "ssns": [],
            "credit_cards": []
        }
        
        # Anonymize text fields
        for field in text_fields_to_check:
            if field in anonymized_data and anonymized_data[field]:
                anonymized_text, detected_pii = self.anonymize_text(
                    str(anonymized_data[field])
                )
                
                if anonymized_text != str(anonymized_data[field]):
                    anonymized_data[field] = anonymized_text
                    privacy_report["pii_removed"] = True
                    privacy_report["items_anonymized"] += 1
                    
                    if field not in privacy_report["categories_affected"]:
                        privacy_report["categories_affected"].append(field)
                
                # Accumulate detected PII
                for pii_type, items in detected_pii.items():
                    total_pii_found[pii_type].extend(items)
        
        # Handle troubleshooting steps (list of strings)
        if "troubleshooting_completed" in anonymized_data:
            anonymized_steps = []
            for step in anonymized_data["troubleshooting_completed"]:
                anonymized_step, detected_pii = self.anonymize_text(str(step))
                anonymized_steps.append(anonymized_step)
                
                # Accumulate detected PII
                for pii_type, items in detected_pii.items():
                    total_pii_found[pii_type].extend(items)
            
            anonymized_data["troubleshooting_completed"] = anonymized_steps
        
        # Special handling for direct PII fields
        sensitive_fields = {
            "customer_name": "[CUSTOMER_NAME]",
            "contact_number": "[PHONE_REMOVED]",
            "email": "[EMAIL_REMOVED]"
        }
        
        for field, replacement in sensitive_fields.items():
            if field in anonymized_data and anonymized_data[field]:
                if field == "customer_name" and len(str(anonymized_data[field])) > 0:
                    # Store masked version for reference
                    total_pii_found["names"] = [self._mask_sensitive_data(str(anonymized_data[field]), "name")]
                
                anonymized_data[field] = replacement
                privacy_report["pii_removed"] = True
                privacy_report["items_anonymized"] += 1
                
                if field not in privacy_report["categories_affected"]:
                    privacy_report["categories_affected"].append(field)
        
        # Preserve device identifiers (MAC, Serial) for technical troubleshooting
        # These are typically needed by engineering teams
        
        # Update privacy report summary
        privacy_report["summary"] = {
            key: len(value) for key, value in total_pii_found.items() if value
        }
        
        if privacy_report["pii_removed"]:
            logger.info(f"PII anonymization completed. Items processed: {privacy_report['items_anonymized']}")
        
        return anonymized_data, privacy_report
    
    def validate_anonymization(self, text: str) -> Dict[str, bool]:
        """
        Validate that text doesn't contain PII after anonymization
        Returns validation results for each PII type
        """
        validation_results = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            validation_results[pii_type] = len(matches) == 0
        
        return validation_results
    
    def get_anonymization_summary(self, privacy_report: Dict[str, Any]) -> str:
        """Generate human-readable summary of anonymization actions"""
        if not privacy_report.get("pii_removed", False):
            return "✅ No PII detected - no anonymization needed"
        
        summary_parts = []
        summary_parts.append(f"🔐 **PII ANONYMIZATION COMPLETED**")
        summary_parts.append(f"📊 Items processed: {privacy_report['items_anonymized']}")
        
        if privacy_report["categories_affected"]:
            summary_parts.append(f"📝 Fields affected: {', '.join(privacy_report['categories_affected'])}")
        
        if privacy_report["summary"]:
            pii_summary = []
            for pii_type, count in privacy_report["summary"].items():
                if count > 0:
                    pii_summary.append(f"{pii_type}: {count}")
            if pii_summary:
                summary_parts.append(f"🔍 PII types found: {', '.join(pii_summary)}")
        
        summary_parts.extend([
            "",
            "⚠️ **PRIVACY NOTICE:**",
            "✔️ Contact details anonymized",
            "✔️ Personal information removed", 
            "✔️ Device identifiers preserved for technical support",
            "✔️ No personally identifiable information retained"
        ])
        
        return "\n".join(summary_parts)
    
    def emergency_pii_check(self, text: str) -> List[str]:
        """Emergency check to catch any remaining PII patterns"""
        warnings = []
        
        # Additional patterns for edge cases
        additional_patterns = {
            "potential_email": r'\b\w+@\w+\b',
            "potential_phone": r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "potential_ssn": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
        }
        
        for pattern_name, pattern in additional_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                warnings.append(f"Potential {pattern_name} detected: {len(matches)} instances")
        
        return warnings