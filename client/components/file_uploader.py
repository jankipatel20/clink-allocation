import io
import streamlit as st
import pandas as pd
<<<<<<< HEAD
import requests

BACKEND_UPLOAD_URL = "http://localhost:8000/upload"

def display_uploader_and_button(nav_right_col):
    """Display file uploader and optimization button"""
    # Initialize session state for history
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
=======
from api_client import BackendAPIClient

def display_uploader_and_button(nav_right_col):
    """Display file uploader and optimization button"""
    # Initialize session state
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
>>>>>>> 57081d4c7b3aa07bfd2b1c69688fcd21748be833
    
    with nav_right_col:
        # Browse Files, Export CSV, History - in one row
        col_btn1, col_btn2, col_btn3 = st.columns([1.1, 1, 1])
        
<<<<<<< HEAD
        # $$ the backend upload logic

        with col_btn1:
            uploaded_files = st.file_uploader(
                "",
                type=["csv", "xls", "xlsx"],
                help="Upload data files (CSV or Excel); they will be sent to the backend",
                label_visibility="collapsed",
                accept_multiple_files=True
            )
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    try:
                        file_bytes = uploaded_file.getvalue()
                        ext = uploaded_file.name.split(".")[-1].lower()
                        buffer = io.BytesIO(file_bytes)

                        if ext == "csv":
                            _ = pd.read_csv(buffer)
                        else:
                            buffer.seek(0)
                            _ = pd.read_excel(buffer)

                        # send to backend
                        try:
                            resp = requests.post(
                                BACKEND_UPLOAD_URL,
                                files={"file": (uploaded_file.name, file_bytes, uploaded_file.type or "application/octet-stream")},
                                timeout=10,
                            )
                            resp.raise_for_status()
                            st.success(f"{uploaded_file.name} uploaded and sent to backend")
                        except Exception as send_err:
                            st.error(f"Uploaded locally but failed to send to backend: {send_err}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
=======
        with col_btn1:
            uploaded_file = st.file_uploader(
                "",
                type=["xlsx"],
                help="Upload Excel file with optimization data",
                label_visibility="collapsed",
                accept_multiple_files=False
            )
            
            # Store uploaded file in session state
            if uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                st.success(f"✓ {uploaded_file.name} ready")
>>>>>>> 57081d4c7b3aa07bfd2b1c69688fcd21748be833
        
        # Export CSV button
        with col_btn2:
            st.button("Export CSV", use_container_width=True)

        # History Toggle button
        with col_btn3:
            if st.button("History", use_container_width=True):
                st.session_state.show_history = not st.session_state.show_history

        # Run Optimization button - separate container below
        st.markdown("""
        <style>
        .run-opt-container button {
            background-color: #FF0000 !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 17px !important;
            padding: 12px 24px !important;
            min-height: 50px !important;
        }
        .run-opt-container button:hover {
            background-color: #C82333 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="run-opt-container">', unsafe_allow_html=True)
        optimize_clicked = st.button("Run Optimization", use_container_width=True, key="run_opt_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        return optimize_clicked

    return False

def handle_optimization():
<<<<<<< HEAD
    """Handle optimization button click"""
    st.success("Optimization started!")
=======
    """Handle optimization button click and call backend"""
    
    # Initialize API client
    api_client = BackendAPIClient()
    
    # Check backend health
    with st.spinner("Connecting to backend..."):
        if not api_client.health_check():
            st.error("❌ Backend is not running. Please start the backend server:\n\n`uvicorn backend.main:app --reload`")
            return
    
    # Run optimization
    with st.spinner("Running optimization... This may take a few minutes."):
        try:
            # Get uploaded file from session state
            uploaded_file = st.session_state.get("uploaded_file")
            
            # Call backend
            result = api_client.run_optimization(uploaded_file)
            
            # Check result status
            if result.get("status") == "success":
                # Store result in session state for display in tabs
                st.session_state.optimization_result = result
                st.session_state.backend_connected = True
                
                st.success("✅ Optimization completed successfully!")
                st.balloons()
                
                # Display key results
                if "total_cost" in result:
                    st.metric("Total Cost", f"₹{result['total_cost']:,.2f}")
                
            elif result.get("status") == "error":
                st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                
            elif result.get("status") == "failed":
                st.warning(f"⚠️ Optimization failed: {result.get('message', 'Solver failed')}")
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
>>>>>>> 57081d4c7b3aa07bfd2b1c69688fcd21748be833
