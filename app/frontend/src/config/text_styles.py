import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the app"""
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2.5rem;
        }
        .main-header p {
            color: rgba(255,255,255,0.9);
            margin-top: 0.5rem;
        }
        .prediction-card {
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .choc-card {
            background-color: #fee;
            border-left: 4px solid #e74c3c;
        }
        .normal-card {
            background-color: #efe;
            border-left: 4px solid #2ecc71;
        }
        .metric-box {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }
        .confidence-high {
            color: #27ae60;
            font-weight: bold;
        }
        .confidence-medium {
            color: #f39c12;
            font-weight: bold;
        }
        .confidence-low {
            color: #e67e22;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)