import pandas as pd
import streamlit as st
from api.model_api import model_api

def render_home():
    """Render home page"""
    st.title("Welcome to GDP Shock Predictor")
    
    st.markdown("""
    ###  What is a GDP Shock?
    
    A GDP shock is an unexpected event that causes significant changes in a country's 
    economic output. Our machine learning model helps predict potential GDP shocks 
    using key macroeconomic indicators.
    
    ###  Features
    
    - **Single Prediction**: Make predictions using individual country data
    - **Batch Processing**: Upload CSV files for bulk predictions
    - **Real-time Analysis**: Get instant results with confidence scores
    - **History Tracking**: Save and review your prediction history
    
    ###  Key Indicators Used
    
    - GDP per capita
    - Government expenditure
    - External debt
    - Unemployment rate
    - Inflation rate
    - Trade openness
    - And more...
    """)
    
    
    st.markdown("---")
    st.subheader("System Status")
    
    health = model_api.get_health()
    if health.get('status') == 'healthy':
        st.success(" Model API is operational")
    else:
        st.error(" Model API is unavailable")
    
    
    model_info = model_api.get_model_info()
    if model_info:
        metrics = model_info.get('metrics', {})
        threshold = model_info.get('optimal_threshold', 0)
    
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Model Type", model_info.get('model_type', 'N/A'))
        with col2:
            st.metric("Sampling Strategy", model_info.get('sampling_strategy', 'N/A'))
        with col3:
            st.metric("Training Date", model_info.get('training_date', 'N/A'))
        with col4:
            st.metric("Version", model_info.get('version', 'N/A'))
    
        st.markdown("---")
    
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Optimal Threshold", f"{threshold:.2f}")
        with col2:
            st.metric("ROC-AUC", f"{metrics.get('roc_auc', 0):.3f}")
        with col3:
            st.metric("F1 Score", f"{metrics.get('f1', 0):.3f}")
        with col4:
            st.metric("Precision", f"{metrics.get('precision', 0):.3f}")
        with col5:
            st.metric("Recall", f"{metrics.get('recall', 0):.3f}")
    
        st.markdown("---")
    
        
        col_left, col_right = st.columns(2)
    
        with col_left:
            features = model_info.get('features', [])
            st.subheader(f"Input Features ({len(features)})")
            st.dataframe(
                pd.DataFrame({"Feature": features}),
                use_container_width=True,
                hide_index=True,
            )
    
        with col_right:
            cm = metrics.get('confusion_matrix')
            if cm:
                st.subheader("Confusion Matrix (Test Set)")
                cm_df = pd.DataFrame(
                    cm,
                    index=["Actual: Normal", "Actual: Choc"],
                    columns=["Predicted: Normal", "Predicted: Choc"],
                )
                st.dataframe(cm_df, use_container_width=True)
    
            # Extra metrics if present
            extra = {k: v for k, v in metrics.items()
                    if k not in ('roc_auc', 'f1', 'precision', 'recall', 'confusion_matrix')}
            if extra:
                st.subheader("Additional Metrics")
                st.dataframe(
                    pd.DataFrame(extra.items(), columns=["Metric", "Value"]),
                    use_container_width=True,
                    hide_index=True,
                )