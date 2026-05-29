import streamlit as st
from api.model_api import model_api

def render_home():
    """Render home page"""
    st.title("Welcome to GDP Shock Predictor")
    
    st.markdown("""
    ###  What is a GDP Shock?
    
    A GDP shock is an unexpected event that causes significant changes in a country's 
    economic output. Our machine learning model helps predict potential GDP shocks 
    using key macroeconomic indicators.
    
    ###  Features
    
    - **Single Prediction**: Make predictions using individual country data
    - **Batch Processing**: Upload CSV files for bulk predictions
    - **Real-time Analysis**: Get instant results with confidence scores
    - **History Tracking**: Save and review your prediction history
    
    ###  Key Indicators Used
    
    - GDP per capita
    - Government expenditure
    - External debt
    - Unemployment rate
    - Inflation rate
    - Trade openness
    - And more...
    """)
    
    # Health check
    st.markdown("---")
    st.subheader("System Status")
    
    health = model_api.get_health()
    if health.get('status') == 'healthy':
        st.success(" Model API is operational")
    else:
        st.error(" Model API is unavailable")
    
    # Model info
    model_info = model_api.get_model_info()
    if model_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model Version", model_info.get('version', 'N/A'))
        with col2:
            st.metric("Last Updated", model_info.get('last_updated', 'N/A'))
        with col3:
            st.metric("Features", len(model_info.get('features', [])))