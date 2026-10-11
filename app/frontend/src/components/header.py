import streamlit as st
from config.constants import APP_NAME, APP_VERSION

def render_header():
    """Render the app header"""
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="main-header">
            <h1>{APP_NAME}</h1>
            <p>Predict GDP shocks using advanced machine learning models</p>
            <small>Version {APP_VERSION}</small>
        </div>
        """, unsafe_allow_html=True)