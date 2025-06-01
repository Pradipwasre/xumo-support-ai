"""
Data handler for processing and managing support tickets
Handles CSV operations, data cleaning, and file management
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self):
        self.config = get_config()
        self.data_dir = self.config["files"]["data_dir"]
        self.ensure_data_directory()
        self.knowledge_base = self.load_knowledge_base()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from JSON file or create default"""
        kb_file = self.config["files"]["knowledge_base"]
        
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading knowledge base: {e}")
                return self.config["knowledge_base"]
        else:
            # Create default knowledge base
            self.save_knowledge_base(self.config["knowledge_base"])
            return self.config["knowledge_base"]
    
    def save_knowledge_base(self, kb_data: Dict[str, Any]):
        """Save knowledge base to JSON file"""
        kb_file = self.config["files"]["knowledge_base"]
        try:
            with open(kb_file, 'w') as f:
                json.dump(kb_data, f, indent=2)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def parse_ticket_text(self, ticket_text: str) -> Dict[str, Any]:
        """Parse raw ticket text into structured data"""
        ticket_data = {
            "timestamp": datetime.now().isoformat(),
            "raw_text": ticket_text,
            "issue_description": "",
            "customer_name": "",
            "contact_number": "",
            "email": "",
            "device_details": {},
            "troubleshooting_completed": [],
            "escalation_status": ""
        }
        
        lines = ticket_text.strip().split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse different sections
            if line.startswith("Issue Description:"):
                ticket_data["issue_description"] = line.replace("Issue Description:", "").strip()
            elif line.startswith("Customer Name:"):
                ticket_data["customer_name"] = line.replace("Customer Name:", "").strip()
            elif line.startswith("Contact Number:"):
                ticket_data["contact_number"] = line.replace("Contact Number:", "").strip()
            elif line.startswith("Email:"):
                ticket_data["email"] = line.replace("Email:", "").strip()
            elif line.startswith("Device Details:"):
                current_section = "device"
            elif line.startswith("Troubleshooting Steps"):
                current_section = "troubleshooting"
            elif line.startswith("MAC Address:"):
                ticket_data["device_details"]["mac_address"] = line.replace("MAC Address:", "").strip()
            elif line.startswith("Serial Number:"):
                ticket_data["device_details"]["serial_number"] = line.replace("Serial Number:", "").strip()
            elif current_section == "troubleshooting" and ("✅" in line or "✔️" in line):
                step = line.replace("✅", "").replace("✔️", "").strip()
                if step:
                    ticket_data["troubleshooting_completed"].append(step)
            elif "escalat" in line.lower():
                ticket_data["escalation_status"] = line.strip()
        
        return ticket_data
    
    def save_raw_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Save raw ticket data to CSV and return ticket ID"""
        raw_file = self.config["files"]["raw_tickets"]
        
        # Generate ticket ID
        ticket_id = f"TKT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ticket_data["ticket_id"] = ticket_id
        
        # Convert to DataFrame
        df_row = pd.DataFrame([ticket_data])
        
        # Append to existing file or create new
        if os.path.exists(raw_file):
            df_existing = pd.read_csv(raw_file)
            df_combined = pd.concat([df_existing, df_row], ignore_index=True)
        else:
            df_combined = df_row
        
        df_combined.to_csv(raw_file, index=False)
        logger.info(f"Saved raw ticket: {ticket_id}")
        
        return ticket_id
    
    def save_processed_ticket(self, ticket_id: str, processed_data: Dict[str, Any]):
        """Save processed ticket data"""
        processed_file = self.config["files"]["processed_tickets"]
        
        processed_data["ticket_id"] = ticket_id
        processed_data["processed_timestamp"] = datetime.now().isoformat()
        
        df_row = pd.DataFrame([processed_data])
        
        if os.path.exists(processed_file):
            df_existing = pd.read_csv(processed_file)
            df_combined = pd.concat([df_existing, df_row], ignore_index=True)
        else:
            df_combined = df_row
        
        df_combined.to_csv(processed_file, index=False)
        logger.info(f"Saved processed ticket: {ticket_id}")
    
    def load_tickets(self, ticket_type: str = "raw") -> Optional[pd.DataFrame]:
        """Load tickets from CSV file"""
        if ticket_type == "raw":
            file_path = self.config["files"]["raw_tickets"]
        else:
            file_path = self.config["files"]["processed_tickets"]
        
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                logger.error(f"Error loading {ticket_type} tickets: {e}")
                return None
        return None
    
    def get_ticket_stats(self) -> Dict[str, Any]:
        """Get statistics about processed tickets"""
        stats = {
            "total_raw_tickets": 0,
            "total_processed_tickets": 0,
            "escalation_rate": 0,
            "common_issues": []
        }
        
        # Raw tickets
        raw_df = self.load_tickets("raw")
        if raw_df is not None:
            stats["total_raw_tickets"] = len(raw_df)
        
        # Processed tickets
        processed_df = self.load_tickets("processed")
        if processed_df is not None:
            stats["total_processed_tickets"] = len(processed_df)
            
            # Calculate escalation rate if escalation data exists
            if "escalation_prediction" in processed_df.columns:
                escalated = processed_df["escalation_prediction"].apply(
                    lambda x: "high" in str(x).lower() if pd.notna(x) else False
                ).sum()
                stats["escalation_rate"] = (escalated / len(processed_df)) * 100
        
        return stats
    
    def search_knowledge_base(self, query: str, category: str = None) -> List[str]:
        """Search knowledge base for relevant troubleshooting steps"""
        results = []
        
        if category and category.lower().replace(" ", "_") in self.knowledge_base:
            kb_section = self.knowledge_base[category.lower().replace(" ", "_")]
            if "common_steps" in kb_section:
                results.extend(kb_section["common_steps"])
        else:
            # Search all categories
            for cat_data in self.knowledge_base.values():
                if isinstance(cat_data, dict) and "common_steps" in cat_data:
                    results.extend(cat_data["common_steps"])
        
        # Filter results based on query relevance (simple keyword matching)
        if query:
            query_words = query.lower().split()
            filtered_results = []
            for step in results:
                if any(word in step.lower() for word in query_words):
                    filtered_results.append(step)
            return filtered_results[:5]  # Return top 5 matches
        
        return results[:5]  # Return first 5 if no specific query
    
    def cleanup_old_tickets(self, days_old: int = 30):
        """Clean up tickets older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for ticket_type in ["raw", "processed"]:
            df = self.load_tickets(ticket_type)
            if df is not None and "timestamp" in df.columns:
                df["timestamp_parsed"] = pd.to_datetime(df["timestamp"])
                df_filtered = df[df["timestamp_parsed"].dt.timestamp() > cutoff_date]
                
                # Save filtered data
                file_path = (self.config["files"]["raw_tickets"] if ticket_type == "raw" 
                           else self.config["files"]["processed_tickets"])
                df_filtered.drop("timestamp_parsed", axis=1).to_csv(file_path, index=False)
                
                removed_count = len(df) - len(df_filtered)
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} old {ticket_type} tickets")