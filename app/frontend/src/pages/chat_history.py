import streamlit as st
import pandas as pd
from api.user_api import user_api
from store.model_store import ModelStore
from datetime import datetime

def render_chat_history():
    """Render chat history page"""
    st.title("Prediction History")
    
    user = ModelStore.get_user()
    if not user:
        st.warning("Please login to view history")
        return
    
    predictions = st.session_state.get("predictions", [])
    
    if not predictions:
        st.info("No prediction history found. Make some predictions to see them here!")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(predictions)
    
    # Format datetime if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", len(df))
    with col2:
        choc_count = len(df[df['prediction'] == 'choc'])
        st.metric("Shock Predictions", choc_count)
    with col3:
        avg_confidence = df['confidence'].map({'high': 1, 'medium': 0.5, 'low': 0.25}).mean() * 100
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    
    st.markdown("---")
    
    # Display history table
    st.subheader("Prediction History")
    
    # Pagination
    items_per_page = 10
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if 'history_page' not in st.session_state:
        st.session_state.history_page = 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if total_pages > 1:
            st.session_state.history_page = st.number_input(
                "Page",
                min_value=0,
                max_value=total_pages-1,
                value=st.session_state.history_page
            )
    
    start_idx = st.session_state.history_page * items_per_page
    end_idx = start_idx + items_per_page
    
    display_df = df.iloc[start_idx:end_idx].copy()
    
    # Select columns to display
    display_columns = ['timestamp', 'prediction', 'probability', 'confidence'] if 'timestamp' in df.columns else ['prediction', 'probability', 'confidence']
    available_cols = [col for col in display_columns if col in display_df.columns]
    
    st.dataframe(
        display_df[available_cols],
        use_container_width=True,
        hide_index=True
    )
    
    # Export option
    if st.button("Export History to CSV", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )