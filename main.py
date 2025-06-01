#!/usr/bin/env python3
"""
Main entry point for the AI Customer Support Assistant
Runs the Streamlit application
"""

import streamlit as st
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui import run_streamlit_app

if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="AI Customer Support Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the Streamlit app
    run_streamlit_app()