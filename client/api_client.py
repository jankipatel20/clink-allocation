"""
API Client for connecting Streamlit frontend to FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, List, Optional, Any


class BackendAPIClient:
    """Client for communicating with the optimization backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """
        Check if the backend is reachable
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
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


# Cache the API client instance
@st.cache_resource
def get_api_client(backend_url: str = "http://localhost:8000") -> BackendAPIClient:
    """
    Get or create a cached API client instance
    
    Args:
        backend_url: URL of the backend API
    
    Returns:
        BackendAPIClient instance
    """
    return BackendAPIClient(backend_url)
