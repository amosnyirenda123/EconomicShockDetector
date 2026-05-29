import streamlit as st
import pandas as pd
import io
from typing import Optional, Dict, Any

def init_session_state():
    """Initialize session state variables"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

def clear_session():
    """Clear all session data"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

def format_prediction_result(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Format prediction results for display"""
    return {
        "prediction": prediction.get("prediction", "unknown"),
        "probability": prediction.get("probability", 0),
        "confidence": prediction.get("confidence", "low"),
        "threshold": prediction.get("threshold", 0.5)
    }

def load_csv_from_bytes(file_bytes: bytes) -> Optional[pd.DataFrame]:
    """Load CSV from bytes"""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def validate_csv_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """Validate CSV has required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return False
    return True

def get_confidence_color(confidence: str) -> str:
    """Return color for confidence level"""
    colors = {
        "high": "#27ae60",
        "medium": "#f39c12",
        "low": "#e67e22"
    }
    return colors.get(confidence, "#95a5a6")