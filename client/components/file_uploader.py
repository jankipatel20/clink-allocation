import io
import streamlit as st
import pandas as pd
from api_client import BackendAPIClient

def convert_result_to_csv(result):
    """Convert optimization result to CSV format"""
    output = io.StringIO()
    
    # Summary Section
    output.write("=== OPTIMIZATION SUMMARY ===\n")
    output.write(f"Status,{result.get('status')}\n")
    output.write(f"Objective Value,{result.get('objective_value')}\n")
    output.write(f"Solver,{result.get('solver')}\n")
    output.write(f"Message,{result.get('message')}\n")
    
    if "summary" in result:
        summary = result["summary"]
        output.write(f"Total Production,{summary.get('total_production')}\n")
        output.write(f"Total Shipments,{summary.get('total_shipments')}\n")
        output.write(f"Total Trips,{summary.get('total_trips')}\n")
        output.write(f"Number of Nodes,{summary.get('num_nodes')}\n")
        output.write(f"Number of Periods,{summary.get('num_periods')}\n")
    
    output.write("\n")
    
    # Production Section
    if result.get("production"):
        output.write("=== PRODUCTION ===\n")
        df_prod = pd.DataFrame(result["production"])
        df_prod.to_csv(output, index=False)
        output.write("\n")
    
    # Shipments Section
    if result.get("shipments"):
        output.write("=== SHIPMENTS ===\n")
        df_ship = pd.DataFrame(result["shipments"])
        df_ship.to_csv(output, index=False)
        output.write("\n")
    
    # Inventory Section
    if result.get("inventory"):
        output.write("=== INVENTORY ===\n")
        df_inv = pd.DataFrame(result["inventory"])
        df_inv.to_csv(output, index=False)
        output.write("\n")
    
    return output.getvalue()

def display_uploader_and_button(nav_right_col):
    """Display file uploader and optimization button"""
    # Initialize session state
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    
    with nav_right_col:
        st.markdown(
            """
            <style>
            /* Align uploader row elements with consistent spacing and size */
            .upload-actions > div button {
                width: 100%;
                padding: 0.75rem 0.9rem;
                font-weight: 600;
            }
            .upload-actions [data-testid="stFileUploaderDropzone"] {
                padding: 0.6rem;
                min-height: 52px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="upload-actions">', unsafe_allow_html=True)
        # Browse Files, Export CSV, History - in one row
        col_btn1, col_btn2, col_btn3 = st.columns(3, gap="small")
        
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
        
        # Export CSV button
        with col_btn2:
            backend_result = st.session_state.get("optimization_result")
            if backend_result and backend_result.get("status") == "success":
                # Convert backend data to CSV
                csv_data = convert_result_to_csv(backend_result)
                st.download_button(
                    label="Export CSV",
                    data=csv_data,
                    file_name=f"optimization_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.button("Export CSV", use_container_width=True, disabled=True, help="Run optimization first")

        # History Toggle button
        with col_btn3:
            if st.button("History", use_container_width=True):
                st.session_state.show_history = not st.session_state.show_history

        st.markdown('</div>', unsafe_allow_html=True)

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
        # Only enable button if a file is uploaded
        has_file = st.session_state.get("uploaded_file") is not None
        if has_file:
            optimize_clicked = st.button("Run Optimization", use_container_width=True, key="run_opt_btn")
        else:
            st.button("Run Optimization", use_container_width=True, key="run_opt_btn", disabled=True, help="Upload a file first")
            optimize_clicked = False
        st.markdown('</div>', unsafe_allow_html=True)
        
        return optimize_clicked

    return False

def handle_optimization():
    """Handle optimization button click and call backend"""
    
    # Get uploaded file from session state
    uploaded_file = st.session_state.get("uploaded_file")
    
    # Check if file is uploaded
    if not uploaded_file:
        st.error("❌ Please upload an Excel file before running optimization")
        return
    
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
            # Call backend with uploaded file
            import sys
            print(f"🔄 Calling /optimize endpoint with file: {uploaded_file.name}", file=sys.stderr, flush=True)
            result = api_client.run_optimization(uploaded_file)
            
            # Log the response
            print("=" * 60, file=sys.stderr, flush=True)
            print("📦 BACKEND RESPONSE FROM /optimize:", file=sys.stderr, flush=True)
            print("=" * 60, file=sys.stderr, flush=True)
            print(f"Status: {result.get('status')}", file=sys.stderr, flush=True)
            print(f"Success: {result.get('success')}", file=sys.stderr, flush=True)
            print(f"Message: {result.get('message')}", file=sys.stderr, flush=True)
            print(f"Objective Value: {result.get('objective_value')}", file=sys.stderr, flush=True)
            
            if "production" in result:
                print(f"Production records: {len(result['production'])}", file=sys.stderr, flush=True)
                if result['production']:
                    print(f"Sample production: {result['production'][0]}", file=sys.stderr, flush=True)
            
            if "shipments" in result:
                print(f"Shipment records: {len(result['shipments'])}", file=sys.stderr, flush=True)
                if result['shipments']:
                    print(f"Sample shipment: {result['shipments'][0]}", file=sys.stderr, flush=True)
            
            if "inventory" in result:
                print(f"Inventory records: {len(result['inventory'])}", file=sys.stderr, flush=True)
                if result['inventory']:
                    print(f"Sample inventory: {result['inventory'][0]}", file=sys.stderr, flush=True)
            
            if "summary" in result:
                print(f"Summary: {result['summary']}", file=sys.stderr, flush=True)
            
            print("=" * 60, file=sys.stderr, flush=True)
            
            # Check result status
            if result.get("status") == "success":
                # Store result in session state for display in tabs
                st.session_state.optimization_result = result
                st.session_state.backend_connected = True
                
                st.success("✅ Optimization completed successfully!")
                st.balloons()
                
                # Display key results
                if "objective_value" in result:
                    st.metric("Total Cost", f"₹{result['objective_value']:,.2f}")
                
            elif result.get("status") == "error":
                st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                print(f"❌ ERROR: {result.get('message', 'Unknown error')}", file=sys.stderr, flush=True)
                
            elif result.get("status") == "failed":
                st.warning(f"⚠️ Optimization failed: {result.get('message', 'Solver failed')}")
                print(f"⚠️ FAILED: {result.get('message', 'Solver failed')}", file=sys.stderr, flush=True)
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            print(f"❌ EXCEPTION: {str(e)}", file=sys.stderr, flush=True)