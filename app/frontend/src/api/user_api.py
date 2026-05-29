import requests
import streamlit as st
from typing import Optional, List, Dict, Any
from types.types import RegisterReq, LoginReq, UserOut, ChatHistoryOut

class UserAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def register(self, user_data: RegisterReq) -> Optional[Dict[str, Any]]:
        """Register new user"""
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json=user_data.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 400:
                st.error("Email already registered or invalid data")
            else:
                st.error(f"Registration failed: {str(e)}")
            return None
    
    def login(self, credentials: LoginReq) -> Optional[Dict[str, Any]]:
        """Login user"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json=credentials.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                st.error("Invalid email or password")
            else:
                st.error(f"Login failed: {str(e)}")
            return None
    
    def get_chat_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's chat history"""
        try:
            response = requests.get(f"{self.base_url}/{user_id}/history")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch chat history: {str(e)}")
            return []


user_api = UserAPI("http://localhost:8000/users")  