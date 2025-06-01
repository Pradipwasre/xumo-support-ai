"""
AI Processor module for GPT integration
Handles communication with OpenAI API for ticket analysis and troubleshooting suggestions
"""

import openai
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config["api"]["openai_key"]
        self.model = self.config["api"]["model"]
        self.max_tokens = self.config["api"]["max_tokens"]
        self.temperature = self.config["api"]["temperature"]
        
        # Initialize OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    
    def _make_gpt_request(self, messages: List[Dict[str, str]], max_tokens: Optional[int] = None) -> Optional[str]:
        """Make request to GPT API with error handling"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
        
        except openai.error.AuthenticationError:
            logger.error("OpenAI authentication failed. Check API key.")
            return None
        except openai.error.RateLimitError:
            logger.error("OpenAI rate limit exceeded. Please try again later.")
            return None
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in GPT request: {e}")
            return None
    
    def analyze_ticket(self, ticket_data: Dict[str, Any], knowledge_base_context: List[str] = None) -> Dict[str, Any]:
        """
        Main function to analyze ticket and generate AI response
        Returns comprehensive analysis including troubleshooting steps and escalation prediction
        """
        if not self.api_key:
            return self._generate_fallback_response(ticket_data)
        
        # Prepare context for GPT
        ticket_summary = self._prepare_ticket_summary(ticket_data)
        kb_context = "\n".join(knowledge_base_context) if knowledge_base_context else ""
        
        # Generate different types of AI responses
        troubleshooting_steps = self._generate_troubleshooting_steps(ticket_summary, kb_context)
        call_script = self._generate_call_script(ticket_summary)
        ticket_update = self._generate_ticket_update(ticket_summary)
        escalation_analysis = self._analyze_escalation_needs(ticket_summary)
        
        # Compile comprehensive response
        ai_response = {
            "ticket_id": ticket_data.get("ticket_id", "Unknown"),
            "analysis_timestamp": datetime.now().isoformat(),
            "troubleshooting_steps": troubleshooting_steps,
            "call_script": call_script,
            "ticket_update": ticket_update,
            "escalation_analysis": escalation_analysis,
            "confidence_score": self._calculate_confidence_score(ticket_data),
            "processing_notes": []
        }
        
        return ai_response
    
    def _prepare_ticket_summary(self, ticket_data: Dict[str, Any]) -> str:
        """Prepare concise ticket summary for GPT processing"""
        summary_parts = []
        
        if ticket_data.get("issue_description"):
            summary_parts.append(f"Issue: {ticket_data['issue_description']}")
        
        if ticket_data.get("device_details"):
            device_info = []
            for key, value in ticket_data["device_details"].items():
                if value:
                    device_info.append(f"{key}: {value}")
            if device_info:
                summary_parts.append(f"Device: {', '.join(device_info)}")
        
        if ticket_data.get("troubleshooting_completed"):
            completed_steps = ticket_data["troubleshooting_completed"]
            if completed_steps:
                summary_parts.append(f"Completed steps: {'; '.join(completed_steps)}")
        
        if ticket_data.get("escalation_status"):
            summary_parts.append(f"Status: {ticket_data['escalation_status']}")
        
        return "\n".join(summary_parts)
    
    def _generate_troubleshooting_steps(self, ticket_summary: str, kb_context: str) -> List[str]:
        """Generate next troubleshooting steps using GPT"""
        system_prompt = self.config["prompts"]["troubleshooting"]
        
        user_prompt = f"""
Ticket Summary:
{ticket_summary}

Available Knowledge Base Steps:
{kb_context}

Please suggest 3-5 specific next troubleshooting steps that haven't been completed yet. 
Be practical and prioritize steps most likely to resolve the issue.
Return only the steps as a numbered list.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_gpt_request(messages, max_tokens=300)
        
        if response:
            # Parse numbered list into clean steps
            steps = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the step text
                    clean_step = line.lstrip('0123456789.-• ').strip()
                    if clean_step:
                        steps.append(clean_step)
            
            return steps[:5] if steps else self._get_default_troubleshooting_steps()
        
        return self._get_default_troubleshooting_steps()
    
    def _generate_call_script(self, ticket_summary: str) -> str:
        """Generate professional call script for agents"""
        user_prompt = f"""
Based on this ticket summary, create a professional call script for a Tier 2 support agent:

{ticket_summary}

The script should be empathetic, professional, and guide the customer through additional troubleshooting.
Include opening, troubleshooting questions, and closing statements.
Keep it concise but thorough.
"""
        
        messages = [
            {"role": "system", "content": "You are creating professional customer service scripts."},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_gpt_request(messages, max_tokens=400)
        
        if response:
            return response
        
        # Fallback script
        return """Hello, this is [Agent Name] from Technical Support. I understand you're experiencing connectivity issues with your device. I'm here to help resolve this for you today.

I can see our previous team has already tried some basic troubleshooting steps. Let's try a few additional steps that often resolve similar issues:

1. Can you confirm if other devices on your network are working properly?
2. Let's try setting up a static IP address for your device
3. Can you run a network diagnostic test for me?

If these steps don't resolve the issue, I'll escalate this to our engineering team with detailed logs to ensure a quick resolution."""
    
    def _generate_ticket_update(self, ticket_summary: str) -> str:
        """Generate structured ticket update format"""
        user_prompt = f"""
Create a structured ticket update based on this information:

{ticket_summary}

Format the update as a professional ticket entry that includes:
- Issue classification
- Steps taken summary
- Current status
- Next recommended actions

Keep it concise and professional for internal team use.
"""
        
        messages = [
            {"role": "system", "content": "Create structured ticket updates for internal team communication."},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_gpt_request(messages, max_tokens=300)
        
        if response:
            return response
        
        # Fallback update
        return """Issue Type: Network Connectivity Problem
Status: In Progress - Additional Troubleshooting Required
Previous Actions: Basic connectivity troubleshooting completed
Next Steps: Advanced network diagnostics and potential escalation to engineering team
Priority: Standard"""
    
    def _analyze_escalation_needs(self, ticket_summary: str) -> Dict[str, Any]:
        """Analyze escalation probability and requirements"""
        user_prompt = f"""
Analyze this support ticket for escalation needs:

{ticket_summary}

Provide:
1. Escalation probability (0-100%)
2. Primary reason for escalation assessment
3. Recommended escalation path (Tier 2, Engineering, Manager, etc.)
4. Urgency level (Low, Medium, High, Critical)

Format as: Probability: X%, Reason: [reason], Path: [path], Urgency: [level]
"""
        
        messages = [
            {"role": "system", "content": self.config["prompts"]["escalation"]},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_gpt_request(messages, max_tokens=200)
        
        escalation_data = {
            "probability": 50,
            "reason": "Standard troubleshooting progression",
            "recommended_path": "Tier 2 Support",
            "urgency": "Medium",
            "confidence": "Medium"
        }
        
        if response:
            # Parse GPT response
            try:
                lines = response.lower()
                
                # Extract probability
                if "probability:" in lines:
                    prob_text = lines.split("probability:")[1].split("%")[0].strip()
                    escalation_data["probability"] = int(float(prob_text.split()[0]))
                
                # Extract reason
                if "reason:" in lines:
                    reason_part = lines.split("reason:")[1].split(",")[0].strip()
                    escalation_data["reason"] = reason_part
                
                # Extract path
                if "path:" in lines:
                    path_part = lines.split("path:")[1].split(",")[0].strip()
                    escalation_data["recommended_path"] = path_part
                
                # Extract urgency
                if "urgency:" in lines:
                    urgency_part = lines.split("urgency:")[1].strip()
                    escalation_data["urgency"] = urgency_part
                
                escalation_data["confidence"] = "High"
                
            except Exception as e:
                logger.warning(f"Error parsing escalation analysis: {e}")
                escalation_data["confidence"] = "Low"
        
        return escalation_data
    
    def _calculate_confidence_score(self, ticket_data: Dict[str, Any]) -> str:
        """Calculate confidence score based on available data quality"""
        score = 0
        max_score = 100
        
        # Issue description quality (30 points)
        if ticket_data.get("issue_description"):
            desc_length = len(str(ticket_data["issue_description"]))
            if desc_length > 50:
                score += 30
            elif desc_length > 20:
                score += 20
            else:
                score += 10
        
        # Device details availability (25 points)
        if ticket_data.get("device_details"):
            device_fields = sum(1 for v in ticket_data["device_details"].values() if v)
            score += min(25, device_fields * 12)
        
        # Troubleshooting history (25 points)
        if ticket_data.get("troubleshooting_completed"):
            steps_count = len(ticket_data["troubleshooting_completed"])
            score += min(25, steps_count * 8)
        
        # Data completeness (20 points)
        required_fields = ["issue_description", "device_details", "troubleshooting_completed"]
        available_fields = sum(1 for field in required_fields if ticket_data.get(field))
        score += (available_fields / len(required_fields)) * 20
        
        percentage = min(100, score)
        
        if percentage >= 80:
            return "High"
        elif percentage >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _get_default_troubleshooting_steps(self) -> List[str]:
        """Fallback troubleshooting steps when GPT is unavailable"""
        return [
            "Verify device network connectivity with ping test",
            "Check DHCP lease and consider static IP assignment",
            "Examine router logs for connection errors",
            "Test with alternative network connection",
            "Contact ISP to verify service status"
        ]
    
    def _generate_fallback_response(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response when GPT API is unavailable"""
        return {
            "ticket_id": ticket_data.get("ticket_id", "Unknown"),
            "analysis_timestamp": datetime.now().isoformat(),
            "troubleshooting_steps": self._get_default_troubleshooting_steps(),
            "call_script": """Hello, I'm calling to follow up on your recent support request. 
            Let's work through some additional troubleshooting steps to resolve your connectivity issue.
            I'll guide you through each step and we'll get this resolved quickly.""",
            "ticket_update": "Standard troubleshooting protocol initiated. Awaiting customer response for next steps.",
            "escalation_analysis": {
                "probability": 50,
                "reason": "API unavailable - using standard assessment",
                "recommended_path": "Tier 2 Support",
                "urgency": "Medium",
                "confidence": "Low"
            },
            "confidence_score": "Low",
            "processing_notes": ["GPT API unavailable - using fallback responses"]
        }
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection and return status"""
        if not self.api_key:
            return {
                "status": "error",
                "message": "API key not configured",
                "suggestion": "Set OPENAI_API_KEY environment variable"
            }
        
        try:
            # Simple test request
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API connection successful'"}
            ]
            
            response = self._make_gpt_request(test_messages, max_tokens=10)
            
            if response:
                return {
                    "status": "success",
                    "message": "API connection successful",
                    "model": self.model
                }
            else:
                return {
                    "status": "error", 
                    "message": "API request failed",
                    "suggestion": "Check API key and network connection"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "suggestion": "Verify API key and try again"
            }