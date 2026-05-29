import streamlit as st
from typing import Dict, Any, Optional

class ModelStore:
    """Global state management for the app"""
    
    @staticmethod
    def set_user(user_data: Dict[str, Any]):
        """Set user data in session"""
        st.session_state.user = user_data
        st.session_state.authenticated = True
    
    @staticmethod
    def get_user() -> Optional[Dict[str, Any]]:
        """Get current user"""
        return st.session_state.get("user", None)
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get("authenticated", False)
    
    @staticmethod
    def logout():
        """Logout user"""
        st.session_state.user = None
        st.session_state.authenticated = False
    
    @staticmethod
    def set_prediction_history(prediction: Dict[str, Any]):
        """Store prediction in history"""
        if "predictions" not in st.session_state:
            st.session_state.predictions = []
        st.session_state.predictions.append(prediction)
    
    @staticmethod
    def get_prediction_history() -> list:
        """Get prediction history"""
        return st.session_state.get("predictions", [])
    
    @staticmethod
    def clear_prediction_history():
        """Clear prediction history"""
        if "predictions" in st.session_state:
            st.session_state.predictions = []