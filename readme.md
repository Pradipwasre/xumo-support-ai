# 🤖 AI Customer Support Assistant

A powerful Streamlit-based AI customer support assistant that processes Zendesk tickets, removes PII (Personally Identifiable Information), suggests troubleshooting steps, and generates structured reports for escalation using GPT-3.5.

## 🌟 Features

- **📥 Ticket Processing**: Paste raw customer support tickets for AI analysis
- **🔐 PII Anonymization**: Automatically removes emails, phone numbers, and other sensitive data
- **🤖 AI-Powered Analysis**: Uses GPT-3.5 to suggest troubleshooting steps and predict escalation needs
- **📊 Multiple Report Types**: Standard, escalation, summary, and engineering reports
- **📞 Call Scripts**: Generated scripts for Tier 2 agents
- **📈 Analytics**: Processing statistics and escalation tracking
- **💾 Data Management**: Persistent storage with CSV export capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (GPT-3.5 access)
- Basic understanding of customer support workflows

### Installation

1. **Clone or download the project files**
```bash
mkdir xumo-support-ai
cd xumo-support-ai
# Copy all the provided Python files into this directory
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**
```bash
# Option 1: Environment variable (recommended)
export OPENAI_API_KEY="your-api-key-here"

# Option 2: Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

4. **Create the data directory structure**
```bash
mkdir data
# The knowledge_base.json file should be placed in the data/ directory
```

5. **Run the application**
```bash
streamlit run main.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
xumo-support-ai/
├── main.py                # Entry point - runs the Streamlit app
├── ui.py                  # Streamlit user interface
├── config.py              # Configuration and API settings
├── data_handler.py        # Data processing and CSV management
├── privacy.py             # PII anonymization module
├── ai_processor.py        # GPT integration and AI processing
├── report_generator.py    # Report formatting and generation
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── data/
    ├── raw_tickets.csv          # Generated: Input tickets with full details
    ├── processed_tickets.csv    # Generated: AI-processed tickets
    └── knowledge_base.json      # Troubleshooting reference database
```

## 🎯 Usage Guide

### Processing a Ticket

1. **Navigate to "🎫 Process Ticket"** in the sidebar
2. **Paste your ticket content** in the text area. Example format:
```
Issue Description: Customer facing network issue with stream box.
Customer Name: Mike Swift
Contact Number: 9896011263
Email: mike.swift@email.com
Device Details:
MAC Address: FD:34:DF:3D:25:00
Serial Number: ES145TGTIG090909

Troubleshooting Steps Completed:
✅ Power cycle performed on stream box & router
✅ Factory reset performed
🚀 Issue still persists, escalating to Tier 2
```

3. **Select processing options**:
   - **Report Type**: Choose from standard, escalation, summary, or engineering
   - **Preserve PII Format**: Keep format of anonymized data
   - **Use Knowledge Base**: Include relevant troubleshooting context

4. **Click "🚀 Process Ticket"** and wait for AI analysis

### Understanding the Output

The AI generates several components:

- **🔍 Troubleshooting Steps**: Specific next actions to resolve the issue
- **📞 Call Script**: Professional script for agent-customer conversations
- **🔁 Ticket Update**: Structured format for updating ticket systems
- **📊 Escalation Analysis**: Probability assessment and recommended escalation path
- **🔐 Privacy Report**: Summary of PII anonymization actions

### Sample AI Output

```
==========================================================
📤 AI-GENERATED OUTPUT: TROUBLESHOOTING & ESCALATION  
==========================================================

🔍 AI-Suggested Next Troubleshooting Steps
----------------------------------------------------------
✔️ Verify MAC address registration with ISP
✔️ Check DHCP settings and assign a static IP
✔️ Run network diagnostics using ping/traceroute

📞 AI-Generated Call Script for Tier 2 Agent
----------------------------------------------------------
"Hello, my name is [Agent Name] from Technical Support.
I see you've been experiencing connectivity issues with your stream box.
Let's go through some additional troubleshooting steps together..."

📊 AI Escalation Prediction Output
----------------------------------------------------------
🔹 Escalation Prediction: 80% chance of requiring Engineering Team
🔹 Urgency Level: High
🔹 Primary Reason: Persistent network failure after standard troubleshooting

🔐 DATA PRIVACY NOTICE
----------------------------------------------------------
✔️ Contact details anonymized
✔️ Device identifiers preserved for technical support
✔️ No personally identifiable information retained
```

## ⚙️ Configuration

### API Settings

The system uses GPT-3.5-turbo for cost optimization. Key settings in `config.py`:

```python
GPT_MODEL = "gpt-3.5-turbo"  # Cost-effective model
GPT_MAX_TOKENS = 1000        # Balanced response length
GPT_TEMPERATURE = 0.3        # Consistent, focused responses
```

### PII Anonymization

The system automatically detects and removes:
- Email addresses → `user@domain.com`
- Phone numbers → `XXX-XXX-XXXX`
- Names → `[CUSTOMER_NAME]`
- SSNs → `XXX-XX-XXXX`
- Credit cards → `XXXX-XXXX-XXXX-XXXX`

Device identifiers (MAC addresses, serial numbers) are preserved for technical troubleshooting.

### Knowledge Base

The `knowledge_base.json` file contains categorized troubleshooting steps:
- Network Issues
- Hardware Problems
- Software Issues
- Account Problems
- Billing Issues
- Streaming Problems

## 💰 Cost Optimization

Designed for efficient API usage with a $4 credit budget:

- **Uses GPT-3.5**: ~10x cheaper than GPT-4
- **Optimized Prompts**: Concise, focused requests
- **Token Limits**: Maximum 1000 tokens per request
- **Batch Processing**: Multiple tickets can be processed in sequence
- **Fallback Responses**: Continues working even if API is unavailable

**Estimated Costs**:
- Simple ticket: ~$0.01-0.02
- Complex ticket: ~$0.03-0.05
- ~100-200 tickets processable with $4 credit

## 📊 Analytics and Reporting

### Built-in Analytics
- Processing statistics
- Escalation rate tracking
- Confidence score distribution
- Session-based analytics

### Export Options
- **Text Format**: Copy-paste ready reports
- **JSON Format**: Structured data for integration
- **Batch Summaries**: Multiple ticket analysis
- **CSV Data**: Raw and processed ticket data

## 🔧 Troubleshooting

### Common Issues

**API Key Problems**:
```bash
# Test your API key
python -c "import openai; openai.api_key='your-key'; print(openai.Model.list())"
```

**Module Import Errors**:
```bash
# Ensure all files are in the same directory
# Check that requirements.txt dependencies are installed
pip install -r requirements.txt
```

**Streamlit Issues**:
```bash
# Clear Streamlit cache
streamlit cache clear
# Restart the application
```

### Testing the Setup

1. **Test API Connection**: Use the "🔍 Test API Connection" button in the sidebar
2. **Process Sample Ticket**: Use the provided example ticket text
3. **Check Data Directory**: Ensure `data/` folder is created and writable

## 🛡️ Privacy and Security

### Data Protection
- **No PII Storage**: All sensitive data is anonymized before processing
- **Local Processing**: Data stays on your system
- **Minimal API Calls**: Only anonymized data sent to OpenAI
- **Audit Trail**: Complete privacy reports for compliance

### Best Practices
- Regularly clean up old ticket data
- Monitor API usage and costs
- Review PII detection patterns periodically
- Use environment variables for API keys

## 🚀 Advanced Usage

### Custom Knowledge Base

Edit `data/knowledge_base.json` to add your organization's specific troubleshooting steps:

```json
{
  "custom_category": {
    "description": "Your specific issue type",
    "common_steps": [
      "Step 1: Your troubleshooting step",
      "Step 2: Another step"
    ],
    "escalation_triggers": [
      "Condition that requires escalation"
    ]
  }
}
```

### Batch Processing

Process multiple tickets by:
1. Processing tickets one by one
2. Using the "📦 Generate Batch Summary" feature
3. Downloading consolidated reports

### Integration

The modular design allows integration with:
- Zendesk API (for automatic ticket ingestion)
- Slack (for notifications)
- Internal ticketing systems
- Reporting dashboards

## 📝 API Reference

### Core Classes

- **`DataHandler`**: Manages ticket data and knowledge base
- **`PIIAnonymizer`**: Handles sensitive data removal
- **`AIProcessor`**: Manages GPT API communication
- **`ReportGenerator`**: Formats output reports
- **`SupportAssistantUI`**: Streamlit interface

### Key Methods

```python
# Process a ticket
processor = AIProcessor()
response = processor.analyze_ticket(ticket_data, kb_context)

# Anonymize PII
anonymizer = PIIAnonymizer()
clean_data, privacy_report = anonymizer.anonymize_ticket_data(ticket_data)

# Generate report
generator = ReportGenerator()
report = generator.generate_complete_report(data, ai_response, privacy_report)
```

## 🤝 Contributing

### Adding Features
1. Follow the modular structure
2. Add new functionality to appropriate modules
3. Update the UI in `ui.py` for user access
4. Test with sample data

### Extending AI Capabilities
- Modify prompts in `config.py`
- Add new analysis functions in `ai_processor.py`
- Create new report types in `report_generator.py`

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review configuration settings
3. Test with sample data
4. Check OpenAI API status and quotas

## 📄 License

This project is provided as-is for educational and commercial use. Please ensure compliance with:
- OpenAI's usage policies
- Your organization's data privacy requirements
- Local data protection regulations

---

**Built with ❤️ for customer support teams everywhere**