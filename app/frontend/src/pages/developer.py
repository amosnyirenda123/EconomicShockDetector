import streamlit as st
from api.model_api import model_api


def render_developers():
    """Render developers / API reference page"""
    st.title("Developers")
    st.markdown("Everything you need to integrate the GDP Shock Prediction API into your application.")

    
    api_info = model_api.get_index()

    base_url = model_api.base_url if hasattr(model_api, 'base_url') else "http://localhost:8000"
    version = api_info.get('version', 'N/A') if api_info else 'N/A'
    description = api_info.get('description', '') if api_info else ''

    
    st.info(f"**{api_info.get('name', 'GDP Shock Prediction API')}** — v{version}\n\n{description}")

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Open Swagger UI", f"{base_url}/docs", use_container_width=True)
    with col2:
        st.link_button("Open ReDoc", f"{base_url}/redoc", use_container_width=True)

    st.markdown("---")

    
    st.subheader("Endpoint Reference")

    endpoints = [
        {
            "method": "GET",
            "path": "/",
            "description": "API overview and links to documentation.",
            "response": '{"name": "...", "version": "...", "description": "...", "docs_url": "/docs"}',
        },
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check. Returns 200 OK when the API and model are operational.",
            "response": '{"status": "ok", "model_loaded": true}',
        },
        {
            "method": "GET",
            "path": "/model/info",
            "description": "Model metadata: type, version, training date, performance metrics, and optimal threshold.",
            "response": '{"model_type": "XGBoost", "optimal_threshold": 0.42, "metrics": {...}}',
        },
        {
            "method": "POST",
            "path": "/predict",
            "description": "Single prediction. Send one observation as JSON, receive prediction + probability.",
            "response": '{"prediction": "choc", "probability": 0.78, "threshold": 0.42, "confidence": "high"}',
        },
        {
            "method": "POST",
            "path": "/predict/batch",
            "description": "Batch prediction. Upload a CSV file, receive an enriched CSV with prediction columns appended.",
            "response": "CSV file with added columns: prediction, probability, threshold, confidence",
        },
    ]

    for ep in endpoints:
        method_color = "green" if ep["method"] == "GET" else "orange"
        with st.expander(f":{method_color}[**{ep['method']}**]  `{ep['path']}`  — {ep['description']}"):
            st.markdown(f"**Base URL:** `{base_url}{ep['path']}`")
            st.markdown(f"**Method:** `{ep['method']}`")
            st.markdown(f"**Description:** {ep['description']}")
            st.markdown("**Example response:**")
            st.code(ep["response"], language="json")

    st.markdown("---")

    
    st.subheader("Quick Start")

    tab_python, tab_curl, tab_js = st.tabs(["Python", "cURL", "JavaScript"])

    with tab_python:
        st.code(f"""
import requests

BASE_URL = "{base_url}"

# Single prediction
payload = {{
    "gdp_per_capita": 3200.0,
    "gov_expenditure": 18.5,
    "unemployment": 14.5,
    "inflation": 8.3,
    "region": "Middle East & North Africa",
    "income_group": "Lower middle income",
    "lending_type": "IBRD",
    "is_crisis_decade": "2010s"
}}
response = requests.post(f"{{BASE_URL}}/predict", json=payload)
print(response.json())

# Batch prediction
with open("observations.csv", "rb") as f:
    response = requests.post(
        f"{{BASE_URL}}/predict/batch",
        files={{"file": ("observations.csv", f, "text/csv")}}
    )
with open("predictions.csv", "wb") as f:
    f.write(response.content)
""", language="python")

    with tab_curl:
        st.code(f"""
# Single prediction
curl -X POST "{base_url}/predict" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "gdp_per_capita": 3200.0,
    "unemployment": 14.5,
    "inflation": 8.3,
    "region": "Middle East & North Africa",
    "income_group": "Lower middle income",
    "lending_type": "IBRD",
    "is_crisis_decade": "2010s"
  }}'

# Batch prediction
curl -X POST "{base_url}/predict/batch" \\
  -F "file=@observations.csv;type=text/csv" \\
  -o predictions.csv
""", language="bash")

    with tab_js:
        st.code(f"""
const BASE_URL = "{base_url}";

// Single prediction
const response = await fetch(`${{BASE_URL}}/predict`, {{
  method: "POST",
  headers: {{ "Content-Type": "application/json" }},
  body: JSON.stringify({{
    gdp_per_capita: 3200.0,
    unemployment: 14.5,
    inflation: 8.3,
    region: "Middle East & North Africa",
    income_group: "Lower middle income",
    lending_type: "IBRD",
    is_crisis_decade: "2010s"
  }})
}});
const result = await response.json();
console.log(result);

// Batch prediction
const formData = new FormData();
formData.append("file", csvFile); // csvFile is a File object
const batchResponse = await fetch(`${{BASE_URL}}/predict/batch`, {{
  method: "POST",
  body: formData
}});
const blob = await batchResponse.blob();
""", language="javascript")