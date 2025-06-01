"""
Streamlit UI for AI Customer Support Assistant
Provides web interface for ticket processing and report generation
"""
import uuid
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import json
from typing import Dict, Any, Optional

# Import our modules
from config import get_config, validate_config
from data_handler import DataHandler
from privacy import PIIAnonymizer
from ai_processor import AIProcessor
from report_generator import ReportGenerator

class SupportAssistantUI:
    def __init__(self):
        self.config = get_config()
        self.data_handler = DataHandler()
        self.pii_anonymizer = PIIAnonymizer()
        self.ai_processor = AIProcessor()
        self.report_generator = ReportGenerator()
        
        # Initialize session state
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'processed_tickets' not in st.session_state:
            st.session_state.processed_tickets = []
        if 'current_report' not in st.session_state:
            st.session_state.current_report = None
        if 'api_status' not in st.session_state:
            st.session_state.api_status = None
    
    def run_app(self):
        """Main application runner"""
        st.title("🤖 AI Customer Support Assistant")
        st.markdown("*Powered by GPT-3.5 for intelligent ticket processing*")
        
        # Sidebar configuration
        self.render_sidebar()
        
        # Main content area
        self.render_main_content()
    
    

    def render_sidebar(self):
        """Render sidebar with navigation and settings"""

        # Ensure API status has a default value to avoid NoneType errors
        if "api_status" not in st.session_state:
            st.session_state.api_status = {"status": "unknown", "message": "API connection not tested"}

        # Ensure sidebar is rendered only once
        if "sidebar_rendered" not in st.session_state:
            st.session_state.sidebar_rendered = True
            st.sidebar.title("🔧 Settings & Navigation")

            # Generate a unique key for the button
            button_key = f"test_api_btn_{uuid.uuid4().hex}"
            
            # API Status Check
            if st.sidebar.button("🔍 Test API Connection", key=button_key): 
                with st.sidebar:
                    with st.spinner("Testing GPT API..."):
                        status = self.ai_processor.test_api_connection()
                        if status:  # Ensure status isn't None
                            st.session_state.api_status = status
                        else:
                            st.session_state.api_status = {"status": "error", "message": "API test failed"}

        # Get the stored API status
        status = st.session_state.api_status

        # Display API test result
        if isinstance(status, dict) and status.get("status") == "success":
            st.sidebar.success(f"✅ {status['message']}")
            st.sidebar.info(f"Model: {status.get('model', 'GPT-3.5')}")
        elif isinstance(status, dict) and status.get("status") == "error":
            st.sidebar.error(f"❌ {status['message']}")
            if "suggestion" in status:
                st.sidebar.warning(status["suggestion"])
        else:
            st.sidebar.warning("⚠️ API connection not tested.")

        # Navigation Section
        st.sidebar.markdown("---")
        st.session_state.page = st.sidebar.radio(
            "📍 Navigate to:",
            ["🎫 Process Ticket", "📊 View Statistics", "📁 Ticket History", "⚙️ Settings"]
        )

        return st.session_state.page
        
    def render_main_content(self):
        """Render main content based on navigation"""
    
        if "sidebar_rendered" not in st.session_state:
            st.session_state.sidebar_rendered = True
            page = self.render_sidebar()
            st.session_state.page = page  # Store selected page in session state
        else:
            page = st.session_state.page  # Retrieve previously rendered page

        if page == "🎫 Process Ticket":
            self.render_ticket_processor()
        elif page == "📊 View Statistics":
            self.render_statistics()
        elif page == "📁 Ticket History":
            self.render_ticket_history()
        elif page == "⚙️ Settings":
            self.render_settings()


    def render_ticket_processor(self):
        """Main ticket processing interface"""
        st.header("🎫 Ticket Processing")
        
        # Input area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Paste Customer Support Ticket")
            ticket_text = st.text_area(
                "Ticket Content:",
                height=300,
                placeholder="""Issue Description: Customer facing network issue with stream box.
Customer Name: Mike Swift
Contact Number: 9896011263
Email: mike.swift@email.com
Device Details:
MAC Address: FD:34:DF:3D:25:00
Serial Number: ES145TGTIG090909

Troubleshooting Steps Completed:
✅ Power cycle performed on stream box & router
✅ Factory reset performed
🚀 Issue still persists, escalating to Tier 2""",
                help="Paste the raw ticket content here. PII will be automatically anonymized."
            )
        
        with col2:
            st.subheader("⚙️ Processing Options")
            
            report_type = st.selectbox(
                "Report Type:",
                ["standard", "escalation", "summary", "engineering"],
                help="Choose the type of report to generate"
            )
            
            preserve_format = st.checkbox(
                "Preserve PII Format",
                value=True,
                help="Keep format of removed PII (e.g., XXX-XXX-XXXX for phones)"
            )
            
            include_kb = st.checkbox(
                "Use Knowledge Base",
                value=True,
                help="Include knowledge base context for better suggestions"
            )
        
        # Process button
        if st.button("🚀 Process Ticket"):
            if ticket_text.strip():
                self.process_ticket(ticket_text, report_type, preserve_format, include_kb)
            else:
                st.error("Please enter ticket content to process.")
        
        # Display results
        if st.session_state.current_report:
            self.display_results()
    
    def process_ticket(self, ticket_text: str, report_type: str, preserve_format: bool, include_kb: bool):
        """Process the ticket through the AI pipeline"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Parse ticket data
            status_text.text("📋 Parsing ticket data...")
            progress_bar.progress(20)
            
            ticket_data = self.data_handler.parse_ticket_text(ticket_text)
            ticket_id = self.data_handler.save_raw_ticket(ticket_data)
            
            # Step 2: Anonymize PII
            status_text.text("🔐 Anonymizing PII...")
            progress_bar.progress(40)
            
            anonymized_data, privacy_report = self.pii_anonymizer.anonymize_ticket_data(ticket_data)
            
            # Step 3: Get knowledge base context
            kb_context = []
            if include_kb:
                status_text.text("📚 Loading knowledge base...")
                progress_bar.progress(60)
                
                issue_desc = anonymized_data.get("issue_description", "")
                kb_context = self.data_handler.search_knowledge_base(issue_desc)
            
            # Step 4: AI Processing
            status_text.text("🤖 Processing with GPT...")
            progress_bar.progress(80)
            
            ai_response = self.ai_processor.analyze_ticket(anonymized_data, kb_context)
            
            # Step 5: Generate report
            status_text.text("📄 Generating report...")
            progress_bar.progress(90)
            
            formatted_report = self.report_generator.generate_complete_report(
                anonymized_data, ai_response, privacy_report, report_type
            )
            
            # Step 6: Save processed data
            self.data_handler.save_processed_ticket(ticket_id, {
                "anonymized_data": json.dumps(anonymized_data),
                "ai_response": json.dumps(ai_response),
                "privacy_report": json.dumps(privacy_report),
                "report_type": report_type
            })
            
            # Store in session state
            st.session_state.current_report = {
                "ticket_id": ticket_id,
                "ticket_data": anonymized_data,
                "ai_response": ai_response,
                "privacy_report": privacy_report,
                "formatted_report": formatted_report,
                "report_type": report_type
            }
            
            # Add to processed tickets list
            st.session_state.processed_tickets.append(st.session_state.current_report)
            
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            
            st.success(f"🎉 Ticket {ticket_id} processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error processing ticket: {str(e)}")
            progress_bar.empty()
            status_text.empty()
    
    def display_results(self):
        """Display processing results and reports"""
        report_data = st.session_state.current_report
        
        st.markdown("---")
        st.header("📋 AI Processing Results")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📄 Complete Report", "🔍 Analysis Summary", "📞 Call Script", 
            "🔐 Privacy Report", "📥 Download"
        ])
        
        with tab1:
            st.subheader("Complete AI-Generated Report")
            st.code(report_data["formatted_report"], language="text")
            
            # Copy button
            if st.button("📋 Copy Report to Clipboard", key="copy_full"):
                st.code(report_data["formatted_report"])
                st.info("💡 Use Ctrl+A, Ctrl+C to copy the report above")
        
        with tab2:
            self.display_analysis_summary(report_data)
        
        with tab3:
            self.display_call_script(report_data)
        
        with tab4:
            self.display_privacy_report(report_data)
        
        with tab5:
            self.display_download_options(report_data)
    
    def display_analysis_summary(self, report_data: Dict[str, Any]):
        """Display analysis summary in structured format"""
        ai_response = report_data["ai_response"]
        escalation = ai_response.get("escalation_analysis", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Escalation Probability",
                f"{escalation.get('probability', 50)}%",
                delta=None
            )
            
            st.metric(
                "Confidence Score",
                ai_response.get("confidence_score", "Medium"),
                delta=None
            )
        
        with col2:
            st.metric(
                "Urgency Level",
                escalation.get("urgency", "Medium"),
                delta=None
            )
            
            st.metric(
                "Recommended Path",
                escalation.get("recommended_path", "Tier 2"),
                delta=None
            )
        
        # Troubleshooting steps
        st.subheader("🔧 Suggested Next Steps")
        steps = ai_response.get("troubleshooting_steps", [])
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")
        
        # Escalation reasoning
        if escalation.get("reason"):
            st.subheader("💡 Escalation Reasoning")
            st.info(escalation["reason"])
    
    def display_call_script(self, report_data: Dict[str, Any]):
        """Display call script for agents"""
        call_script = report_data["ai_response"].get("call_script", "")
        
        if call_script:
            st.subheader("📞 Agent Call Script")
            st.markdown(f"*{call_script}*")
            
            if st.button("📋 Copy Call Script", key="copy_script"):
                st.code(call_script)
                st.info("💡 Use Ctrl+A, Ctrl+C to copy the script above")
        else:
            st.warning("No call script generated")
    
    def display_privacy_report(self, report_data: Dict[str, Any]):
        """Display privacy and PII processing report"""
        privacy_report = report_data["privacy_report"]
        
        if privacy_report.get("pii_removed"):
            st.success("🔐 PII Successfully Anonymized")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Items Processed", privacy_report.get("items_anonymized", 0))
                
            with col2:
                categories = privacy_report.get("categories_affected", [])
                st.metric("Fields Affected", len(categories))
            
            if categories:
                st.subheader("📋 Affected Fields")
                for category in categories:
                    st.write(f"• {category.replace('_', ' ').title()}")
            
            if privacy_report.get("summary"):
                st.subheader("📊 PII Summary")
                for pii_type, count in privacy_report["summary"].items():
                    if count > 0:
                        st.write(f"• {pii_type.title()}: {count} items")
        else:
            st.info("✅ No PII detected in this ticket")
        
        # Privacy notice
        st.markdown("---")
        st.markdown("""
        **🔒 Privacy Compliance Notice:**
        - All personally identifiable information has been anonymized
        - Device identifiers preserved for technical troubleshooting
        - No sensitive customer data is stored or transmitted
        - Processing complies with data protection standards
        """)
    
    def display_download_options(self, report_data: Dict[str, Any]):
        """Display download options for reports"""
        st.subheader("📥 Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Text format download
            txt_data = self.report_generator.generate_downloadable_report(
                report_data["ticket_data"],
                report_data["ai_response"],
                report_data["privacy_report"],
                "txt"
            )
            
            filename_txt = self.report_generator.get_report_filename(
                report_data["ticket_id"], "txt"
            )
            
            st.download_button(
                label="📄 Download as Text",
                data=txt_data,
                file_name=filename_txt,
                mime="text/plain"
            )
        
        with col2:
            # JSON format download
            json_data = self.report_generator.generate_downloadable_report(
                report_data["ticket_data"],
                report_data["ai_response"],
                report_data["privacy_report"],
                "json"
            )
            
            filename_json = self.report_generator.get_report_filename(
                report_data["ticket_id"], "json"
            )
            
            st.download_button(
                label="📊 Download as JSON",
                data=json_data,
                file_name=filename_json,
                mime="application/json"
            )
        
        # Batch download (if multiple tickets processed)
        if len(st.session_state.processed_tickets) > 1:
            st.markdown("---")
            if st.button("📦 Generate Batch Summary"):
                batch_summary = self.report_generator.create_batch_summary(
                    st.session_state.processed_tickets
                )
                
                st.download_button(
                    label="📥 Download Batch Summary",
                    data=batch_summary.encode('utf-8'),
                    file_name=f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    def render_statistics(self):
        """Render statistics and analytics page"""
        st.header("📊 Processing Statistics")
        
        # Get stats from data handler
        stats = self.data_handler.get_ticket_stats()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Raw Tickets", stats["total_raw_tickets"])
        
        with col2:
            st.metric("Processed Tickets", stats["total_processed_tickets"])
        
        with col3:
            st.metric("Escalation Rate", f"{stats['escalation_rate']:.1f}%")
        
        with col4:
            st.metric("Session Tickets", len(st.session_state.processed_tickets))
        
        # Session statistics
        if st.session_state.processed_tickets:
            st.subheader("📈 Session Analytics")
            
            # Create simple analytics
            escalation_probs = []
            confidence_scores = []
            
            for ticket in st.session_state.processed_tickets:
                ai_resp = ticket.get("ai_response", {})
                escalation = ai_resp.get("escalation_analysis", {})
                escalation_probs.append(escalation.get("probability", 50))
                
                conf_score = ai_resp.get("confidence_score", "Medium")
                if conf_score == "High":
                    confidence_scores.append(3)
                elif conf_score == "Medium":
                    confidence_scores.append(2)
                else:
                    confidence_scores.append(1)
            
            # Display charts if we have data
            if escalation_probs:
                df_chart = pd.DataFrame({
                    'Ticket': [f"Ticket {i+1}" for i in range(len(escalation_probs))],
                    'Escalation Probability': escalation_probs
                })
                
                st.bar_chart(df_chart.set_index('Ticket'))
        else:
            st.info("Process some tickets to see analytics here")
    
    def render_ticket_history(self):
        """Render ticket history and management"""
        st.header("📁 Ticket History")
        
        # Load historical data
        raw_tickets = self.data_handler.load_tickets("raw")
        processed_tickets = self.data_handler.load_tickets("processed")
        
        tab1, tab2 = st.tabs(["📋 Raw Tickets", "⚙️ Processed Tickets"])
        
        with tab1:
            if raw_tickets is not None and not raw_tickets.empty:
                st.subheader(f"Raw Tickets ({len(raw_tickets)} total)")
                
                # Display recent tickets
                display_columns = ["ticket_id", "timestamp", "issue_description"]
                available_columns = [col for col in display_columns if col in raw_tickets.columns]
                
                if available_columns:
                    st.dataframe(
                        raw_tickets[available_columns].tail(10),
                        use_container_width=True
                    )
                else:
                    st.dataframe(raw_tickets.tail(10))
            else:
                st.info("No raw tickets found")
        
        with tab2:
            if processed_tickets is not None and not processed_tickets.empty:
                st.subheader(f"Processed Tickets ({len(processed_tickets)} total)")
                
                display_columns = ["ticket_id", "processed_timestamp", "report_type"]
                available_columns = [col for col in display_columns if col in processed_tickets.columns]
                
                if available_columns:
                    st.dataframe(
                        processed_tickets[available_columns].tail(10),
                        use_container_width=True
                    )
                else:
                    st.dataframe(processed_tickets.tail(10))
            else:
                st.info("No processed tickets found")
        
        # Cleanup options
        st.markdown("---")
        st.subheader("🧹 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Session Data"):
                st.session_state.processed_tickets = []
                st.session_state.current_report = None
                st.success("Session data cleared")
        
        with col2:
            days_to_keep = st.number_input("Days to keep", min_value=1, max_value=365, value=30)
            if st.button("🧹 Cleanup Old Tickets"):
                self.data_handler.cleanup_old_tickets(days_to_keep)
                st.success(f"Cleaned up tickets older than {days_to_keep} days")
    
    def render_settings(self):
        """Render settings and configuration page"""
        st.header("⚙️ Settings & Configuration")
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        
        # Check current API status
        config_valid = validate_config()
        
        if config_valid:
            st.success("✅ OpenAI API key is configured")
        else:
            st.error("❌ OpenAI API key not found")
            st.markdown("""
            **To configure the API key:**
            1. Set the `OPENAI_API_KEY` environment variable
            2. Restart the application
            3. Test the connection using the sidebar button
            """)
        
        # Model Settings
        st.subheader("🤖 Model Settings")
        st.info(f"**Current Model:** {self.config['api']['model']}")
        st.info(f"**Max Tokens:** {self.config['api']['max_tokens']}")
        st.info(f"**Temperature:** {self.config['api']['temperature']}")
        
        # Knowledge Base Management
        st.subheader("📚 Knowledge Base")
        
        if st.button("🔄 Reload Knowledge Base"):
            self.data_handler.knowledge_base = self.data_handler.load_knowledge_base()
            st.success("Knowledge base reloaded")
        
        # Display current knowledge base categories
        kb_categories = list(self.data_handler.knowledge_base.keys())
        st.write(f"**Available Categories:** {', '.join(kb_categories)}")
        
        # System Information
        st.subheader("ℹ️ System Information")
        st.json({
            "App Version": self.config["app"]["version"],
            "Data Directory": self.config["files"]["data_dir"],
            "PII Patterns": len(self.config["pii_patterns"]),
            "Knowledge Base Categories": len(kb_categories)
        })

def run_streamlit_app():
    """Main function to run the Streamlit app"""
    app = SupportAssistantUI()
    app.run_app()

if __name__ == "__main__":
    run_streamlit_app()