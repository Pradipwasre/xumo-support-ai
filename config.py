"""
Configuration file for AI Customer Support Assistant
Contains API keys, settings, and application constants
"""

import os
from typing import Dict, Any

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# GPT Model Configuration
GPT_MODEL = "gpt-3.5-turbo"  # Using GPT-3.5 for cost optimization
GPT_MAX_TOKENS = 1000
GPT_TEMPERATURE = 0.3  # Lower temperature for more consistent responses

# Application Settings
APP_TITLE = "AI Customer Support Assistant"
APP_VERSION = "1.0.0"

# File Paths
DATA_DIR = "data"
RAW_TICKETS_FILE = os.path.join(DATA_DIR, "raw_tickets.csv")
PROCESSED_TICKETS_FILE = os.path.join(DATA_DIR, "processed_tickets.csv")
KNOWLEDGE_BASE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")

# PII Patterns for anonymization
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    "ssn": r'\b\d{3}-?\d{2}-?\d{4}\b',
    "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
}

# Troubleshooting Categories
TROUBLESHOOTING_CATEGORIES = [
    "Network Connectivity",
    "Hardware Issues", 
    "Software Problems",
    "Account Issues",
    "Billing Problems",
    "General Inquiry"
]

# Escalation Thresholds
ESCALATION_KEYWORDS = [
    "escalate", "tier 2", "engineering", "unresolved", "persistent",
    "critical", "urgent", "manager", "supervisor", "complaint"
]

# System Prompts for GPT
SYSTEM_PROMPTS = {
    "troubleshooting": """You are an expert customer support AI assistant. Analyze the support ticket and provide:
1. Suggested next troubleshooting steps
2. Call script for the agent
3. Structured ticket update format
4. Escalation prediction with confidence score

Be concise, practical, and professional. Focus on actionable solutions.""",
    
    "escalation": """Analyze this support ticket and predict escalation needs. Consider:
- Issue complexity
- Previous troubleshooting attempts
- Customer sentiment
- Technical requirements

Provide escalation probability (0-100%) and reasoning."""
}

# Default Knowledge Base Structure
DEFAULT_KNOWLEDGE_BASE = {
    "network_issues": {
        "common_steps": [
            "Verify MAC address registration with ISP",
            "Check DHCP settings and assign static IP",
            "Run network diagnostics (ping/traceroute)",
            "Power cycle modem and router",
            "Check cable connections"
        ],
        "escalation_triggers": ["intermittent connectivity", "packet loss", "ISP issues"]
    },
    "hardware_issues": {
        "common_steps": [
            "Perform device restart",
            "Check physical connections",
            "Verify power supply",
            "Test with different cables",
            "Factory reset if necessary"
        ],
        "escalation_triggers": ["hardware failure", "device not responding", "multiple device issues"]
    },
    "software_issues": {
        "common_steps": [
            "Clear cache and cookies",
            "Update software/firmware",
            "Check system requirements",
            "Reinstall application",
            "Reset to default settings"
        ],
        "escalation_triggers": ["software bug", "compatibility issues", "system crashes"]
    }
}

def get_config() -> Dict[str, Any]:
    """Return complete configuration dictionary"""
    return {
        "api": {
            "openai_key": OPENAI_API_KEY,
            "model": GPT_MODEL,
            "max_tokens": GPT_MAX_TOKENS,
            "temperature": GPT_TEMPERATURE
        },
        "app": {
            "title": APP_TITLE,
            "version": APP_VERSION
        },
        "files": {
            "data_dir": DATA_DIR,
            "raw_tickets": RAW_TICKETS_FILE,
            "processed_tickets": PROCESSED_TICKETS_FILE,
            "knowledge_base": KNOWLEDGE_BASE_FILE
        },
        "pii_patterns": PII_PATTERNS,
        "categories": TROUBLESHOOTING_CATEGORIES,
        "escalation_keywords": ESCALATION_KEYWORDS,
        "prompts": SYSTEM_PROMPTS,
        "knowledge_base": DEFAULT_KNOWLEDGE_BASE
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    if not OPENAI_API_KEY:
        return False
    return True