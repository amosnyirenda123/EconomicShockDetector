import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from api.model_api import model_api
from store.model_store import ModelStore
from types.types import PredictRequest
from config.constants import REGIONS, INCOME_GROUPS, LENDING_TYPES, CRISIS_DECADES

def render_single_prediction():
    """Render single prediction interface"""
    st.title("Single Prediction")
    st.markdown("Enter macroeconomic indicators to predict GDP shock")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            gdp_per_capita = st.number_input(
                "GDP per capita (USD)",
                min_value=0.0,
                value=3200.0,
                help="Gross Domestic Product per capita in US dollars"
            )
            
            gov_expenditure = st.number_input(
                "Government expenditure (% of GDP)",
                min_value=0.0,
                value=18.5,
                help="Government expenditure as percentage of GDP"
            )
            
            debt_service_pct = st.number_input(
                "Debt service (% of GNI)",
                min_value=0.0,
                value=12.0,
                help="Debt service as percentage of Gross National Income"
            )
            
            external_debt_pct = st.number_input(
                "External debt (% of GNI)",
                min_value=0.0,
                value=55.0,
                help="External debt stocks as percentage of GNI"
            )
            
            gni_per_capita_growth = st.number_input(
                "GNI per capita growth (annual %)",
                value=-2.1,
                help="Annual growth rate of GNI per capita"
            )
            
            unemployment = st.number_input(
                "Unemployment rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=14.5,
                help="Percentage of labor force that is unemployed"
            )
        
        with col2:
            fx_reserves_months = st.number_input(
                "FX reserves (months of imports)",
                min_value=0.0,
                value=2.1,
                help="Foreign exchange reserves in months of imports"
            )
            
            current_account_pct = st.number_input(
                "Current account balance (% of GDP)",
                value=-6.5,
                help="Current account balance as percentage of GDP"
            )
            
            trade_openness = st.number_input(
                "Trade openness (% of GDP)",
                min_value=0.0,
                value=72.0,
                help="Total trade as percentage of GDP"
            )
            
            inflation = st.number_input(
                "Inflation rate (%)",
                value=8.3,
                help="Consumer price inflation rate"
            )
            
            fdi_inflows = st.number_input(
                "FDI inflows (% of GDP)",
                min_value=0.0,
                value=1.2,
                help="Foreign Direct Investment inflows as percentage of GDP"
            )
        
        # Categorical variables
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            region = st.selectbox("Region", REGIONS)
        with col2:
            income_group = st.selectbox("Income Group", INCOME_GROUPS)
        with col3:
            lending_type = st.selectbox("Lending Type", LENDING_TYPES)
        with col4:
            is_crisis_decade = st.selectbox("Decade", CRISIS_DECADES)
        
        submitted = st.form_submit_button("🔮 Predict", use_container_width=True)
        
        if submitted:
            # Create prediction request
            request = PredictRequest(
                gdp_per_capita=gdp_per_capita,
                gov_expenditure=gov_expenditure,
                debt_service_pct=debt_service_pct,
                external_debt_pct=external_debt_pct,
                gni_per_capita_growth=gni_per_capita_growth,
                unemployment=unemployment,
                fx_reserves_months=fx_reserves_months,
                current_account_pct=current_account_pct,
                trade_openness=trade_openness,
                inflation=inflation,
                fdi_inflows=fdi_inflows,
                region=region,
                income_group=income_group,
                lending_type=lending_type,
                is_crisis_decade=is_crisis_decade
            )
            
            with st.spinner("Making prediction..."):
                result = model_api.predict_single(request)
                
                if result:
                    # Add timestamp to result
                    result['timestamp'] = datetime.now()
                    
                    # Store in history
                    ModelStore.set_prediction_history(result)
                    
                    # Display results
                    display_prediction_results(result)

def display_prediction_results(result):
    """Display prediction results with visualizations"""
    st.markdown("---")
    st.subheader("Prediction Results")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Prediction",
            result['prediction'].upper(),
            delta="Shock Event" if result['prediction'] == 'choc' else "Normal",
            delta_color="inverse" if result['prediction'] == 'choc' else "normal"
        )
    with col2:
        st.metric("Probability", f"{result['probability']:.1%}")
    with col3:
        st.metric("Confidence", result['confidence'].upper())
    
    # Gauge chart for probability
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=result['probability'] * 100,
        title={'text': "Shock Probability"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#ff7f0e"},
            'steps': [
                {'range': [0, 33], 'color': "#2ecc71"},
                {'range': [33, 66], 'color': "#f39c12"},
                {'range': [66, 100], 'color': "#e74c3c"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': result['threshold'] * 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    st.markdown("---")
    st.subheader("Interpretation")
    
    if result['prediction'] == 'choc':
        st.warning(f"""
        **GDP Shock Detected**
        
        The model predicts a potential GDP shock with {result['confidence']} confidence.
        The probability of a shock event is {result['probability']:.1%}, which exceeds 
        the threshold of {result['threshold']:.1%}.
        
        Recommended actions:
        - Monitor key indicators closely
        - Consider risk mitigation strategies
        - Review economic policies
        """)
    else:
        st.success(f"""
        **Normal Economic Conditions**
        
        The model predicts normal economic conditions with {result['confidence']} confidence.
        The probability of a shock is {result['probability']:.1%}, which is below 
        the threshold of {result['threshold']:.1%}.
        
        Current outlook appears stable.
        """)