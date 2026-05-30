import io

import requests
import streamlit as st
from typing import Dict, Any, Optional
from prediction_types import PredictRequest, PredictResponse

class ModelAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url


    def get_index(self) -> Optional[dict]:
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach API: {str(e)}")
            return None
    
    def get_health(self) -> Dict[str, Any]:
        """Check model API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Health Check Failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        try:
            response = requests.get(f"{self.base_url}/model/info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get model info: {str(e)}")
            return {}
    
    def predict_single(self, request: PredictRequest) -> Optional[Dict[str, Any]]:
        """Make single prediction"""
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Prediction failed: {str(e)}")
            return None
    
    def predict_batch(self, file_bytes: bytes, filename: str) -> Optional[bytes]:
        try:
            response = requests.post(
                f"{self.base_url}/predict/batch",
                files={"file": (filename, file_bytes, "text/csv")}
            )
            response.raise_for_status()
            return io.BytesIO(response.content)  # return BytesIO so pd.read_csv works directly
        except requests.exceptions.RequestException as e:
            st.error(f"Batch prediction failed: {str(e)}")
            return None


model_api = ModelAPI("http://localhost:8000")  