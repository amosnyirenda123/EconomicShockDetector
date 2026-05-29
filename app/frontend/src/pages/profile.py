import streamlit as st
from store.model_store import ModelStore
from datetime import datetime

def render_profile():
    """Render user profile page"""
    st.title("User Profile")
    
    user = ModelStore.get_user()
    if not user:
        st.warning("Please login to view profile")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Personal Information")
        st.write(f"**First Name:** {user.get('firstname', 'N/A')}")
        st.write(f"**Last Name:** {user.get('lastname', 'N/A')}")
        st.write(f"**Email:** {user.get('email', 'N/A')}")
        
        if user.get('date_of_birth'):
            dob = datetime.fromisoformat(user['date_of_birth'].replace('Z', '+00:00'))
            st.write(f"**Date of Birth:** {dob.strftime('%Y-%m-%d')}")
    
    with col2:
        st.markdown("### Account Statistics")
        predictions = st.session_state.get("predictions", [])
        st.metric("Total Predictions", len(predictions))
        
        if predictions:
            choc_count = sum(1 for p in predictions if p.get('prediction') == 'choc')
            st.metric("Shock Events Predicted", choc_count)
    
    st.markdown("---")
    
    if st.button("Refresh", use_container_width=True):
        st.rerun()