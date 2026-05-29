import streamlit as st
from store.model_store import ModelStore

def render_sidebar():
    """Render the sidebar with navigation and user info"""
    with st.sidebar:
        st.markdown("## Navigation")
        
        # Navigation buttons
        if st.button("Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("Single Prediction", use_container_width=True):
            st.session_state.current_page = "single_prediction"
            st.rerun()
        
        if st.button("Batch Prediction", use_container_width=True):
            st.session_state.current_page = "batch_prediction"
            st.rerun()
        
        st.markdown("---")
        
        # User section
        if ModelStore.is_authenticated():
            user = ModelStore.get_user()
            st.markdown(f"### {user.get('firstname', 'User')}")
            st.markdown(f"{user.get('email', '')}")
            
            if st.button("Chat History", use_container_width=True):
                st.session_state.current_page = "chat_history"
                st.rerun()
            
            if st.button("Profile", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
            
            if st.button("Logout", use_container_width=True):
                ModelStore.logout()
                st.rerun()
        else:
            if st.button("Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
            
            if st.button("Register", use_container_width=True):
                st.session_state.current_page = "register"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool predicts GDP shocks using:
        - Macroeconomic indicators
        - World Bank data
        - Machine learning models
        """)