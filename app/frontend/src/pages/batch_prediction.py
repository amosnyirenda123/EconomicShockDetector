import io

import streamlit as st
import pandas as pd
from datetime import datetime
from api.model_api import model_api

def render_batch_prediction():
    """Render batch prediction interface"""
    st.title("Batch Prediction")
    st.markdown("Upload a CSV file containing multiple observations for bulk prediction")
 
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="File must contain all required feature columns"
    )
 
    if uploaded_file:
        st.info(f"File: {uploaded_file.name} | Size: {uploaded_file.size / 1024:.2f} KB")
 
        try:
            # Always read via BytesIO — Streamlit UploadedFile can behave like bytes
            raw_bytes = uploaded_file.read()
            df_preview = pd.read_csv(io.BytesIO(raw_bytes))
 
            st.subheader("Data Preview")
            st.dataframe(df_preview.head(), use_container_width=True)
            st.caption(f"Total rows: {len(df_preview)}")
 
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Run Batch Prediction", use_container_width=True):
                    # Pass raw_bytes directly — no second read needed
                    process_batch_prediction(raw_bytes, uploaded_file.name)
            with col2:
                if st.button("Clear", use_container_width=True):
                    st.rerun()
 
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

def process_batch_prediction(file_bytes: bytes, filename: str):
    """Process batch prediction"""
    with st.spinner("Processing batch predictions..."):
        result_bytes = model_api.predict_batch(file_bytes, filename)
        
        if result_bytes:
            # Load results
            result_df = pd.read_csv(result_bytes)
            
            # Display results
            st.markdown("---")
            st.subheader("Batch Prediction Results")
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                shock_count = len(result_df[result_df['prediction'] == 'choc'])
                st.metric("Shock Events", shock_count)
            with col2:
                normal_count = len(result_df[result_df['prediction'] == 'normal'])
                st.metric("Normal Events", normal_count)
            with col3:
                avg_prob = result_df['probability'].mean()
                st.metric("Avg Probability", f"{avg_prob:.1%}")
            with col4:
                high_conf = len(result_df[result_df['confidence'] == 'high'])
                st.metric("High Confidence", high_conf)
            
            # Display results table
            st.subheader("Detailed Results")
            st.dataframe(result_df, use_container_width=True)
            
            # Download button
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name=f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Store in history (as a batch)
            batch_result = {
                'timestamp': datetime.now(),
                'type': 'batch',
                'filename': filename,
                'total_predictions': len(result_df),
                'shock_count': shock_count
            }
            
            # Optional: Store batch summary in history
            if "batch_history" not in st.session_state:
                st.session_state.batch_history = []
            st.session_state.batch_history.append(batch_result)