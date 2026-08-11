"""
API Client for connecting Streamlit frontend to FastAPI backend
"""
import os
import requests
import streamlit as st
from typing import Dict, List, Optional, Any

# Check st.secrets first (for Streamlit Cloud), then os.environ (for Docker), then fallback to localhost
try:
    _DEFAULT_BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
except Exception:
    _DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class BackendAPIClient:
    """Client for communicating with the optimization backend"""
    
    def __init__(self, base_url: str = _DEFAULT_BACKEND_URL):
        """
        Initialize the API client

        Args:
            base_url: Base URL of the FastAPI backend.
                      Defaults to BACKEND_URL env var or http://localhost:8000.
        """
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """
        Check if the backend is reachable
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            # Render free tier can take up to 50s to wake up from sleep
            response = requests.get(f"{self.base_url}/health", timeout=60)
            return response.status_code == 200 and response.json().get("status") == "ok"
        except requests.exceptions.RequestException:
            return False
    
    def run_optimization(self, uploaded_file: Optional[Any] = None) -> Dict[str, Any]:
        """
        Send optimization request to backend
        
        Args:
            uploaded_file: Optional Streamlit UploadedFile object (Excel file)
                          If None, backend will use default Excel file
        
        Returns:
            Dictionary containing optimization results:
            {
                "status": "success" | "error" | "failed",
                "total_cost": float,
                "production": [...],
                "inventory": [...],
                "shipments": [...],
                "message": str (if error)
            }
        """
        try:
            if uploaded_file:
                # Prepare Excel file for upload
                uploaded_file.seek(0)
                files = {
                    "file": (uploaded_file.name, uploaded_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                }
                
                response = requests.post(
                    f"{self.base_url}/optimize",
                    files=files,
                    timeout=300  # 5 minutes timeout for optimization
                )
            else:
                # No file, backend will use default Excel
                response = requests.post(
                    f"{self.base_url}/optimize",
                    timeout=300
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"Server returned status code {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Request timed out. Optimization may be taking too long."
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to backend. Make sure it's running on " + self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }

    def get_history(self) -> Dict[str, Any]:
        """
        Fetch the list of past optimization runs from the backend

        Returns:
            Dictionary with a 'runs' key containing a list of run records,
            or an error dict if the request fails.
        """
        try:
            response = requests.get(f"{self.base_url}/history", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"runs": [], "error": f"Server returned {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"runs": [], "error": "Cannot connect to backend"}
        except Exception as e:
            return {"runs": [], "error": str(e)}


# Cache the API client instance
@st.cache_resource
def get_api_client(backend_url: str = _DEFAULT_BACKEND_URL) -> BackendAPIClient:
    """
    Get or create a cached API client instance
    
    Args:
        backend_url: URL of the backend API
    
    Returns:
        BackendAPIClient instance
    """
    return BackendAPIClient(backend_url)
