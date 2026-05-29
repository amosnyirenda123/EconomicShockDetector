import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar
from components.footer import render_footer

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="GDP Shock Predictor",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_layout(content_function):
    """Render the main app layout"""
    setup_page_config()
    
    # Apply custom styles
    from config.text_styles import apply_custom_styles
    apply_custom_styles()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    with st.container():
        render_header()
        content_function()
        render_footer()