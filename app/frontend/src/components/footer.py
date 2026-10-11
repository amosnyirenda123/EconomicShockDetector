import streamlit as st

def render_footer():
    """Render the app footer"""
    st.markdown("---")
    _, col2, _ = st.columns(3)
    
    with col2:
        st.markdown(
            """
            <div style="text-align: center; color: #7f8c8d;">
                <small>
                    © 2026 GDP Shock Predictor | Powered by ENSA Tetouan
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )