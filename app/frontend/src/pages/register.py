import streamlit as st
from datetime import datetime, date
from api.user_api import user_api
from types.types import RegisterReq

def render_register():
    """Render registration page"""
    st.title("Create Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            firstname = st.text_input("First Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
        
        with col2:
            lastname = st.text_input("Last Name")
            date_of_birth = st.date_input(
                "Date of Birth",
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register", use_container_width=True)
        
        if submitted:
            if not all([firstname, lastname, email, password, date_of_birth]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                register_req = RegisterReq(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    password=password,
                    date_of_birth=datetime.combine(date_of_birth, datetime.min.time())
                )
                
                user_data = user_api.register(register_req)
                if user_data:
                    st.success("Registration successful! Please login.")
                    st.session_state.current_page = "login"
                    st.rerun()