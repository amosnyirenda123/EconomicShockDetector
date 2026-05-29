import streamlit as st
from api.user_api import user_api
from store.model_store import ModelStore
from types.types import LoginReq

def render_login():
    """Render login page"""
    st.title("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True)
        with col2:
            if st.form_submit_button("Register", use_container_width=True):
                st.session_state.current_page = "register"
                st.rerun()
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                login_req = LoginReq(email=email, password=password)
                user_data = user_api.login(login_req)
                
                if user_data:
                    ModelStore.set_user(user_data)
                    st.success(f"Welcome back, {user_data['firstname']}!")
                    st.session_state.current_page = "home"
                    st.rerun()