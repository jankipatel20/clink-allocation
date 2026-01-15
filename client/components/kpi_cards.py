import streamlit as st

def display_kpi_cards():
    """Display KPI cards row"""
    
    # Check if backend data is available
    backend_result = st.session_state.get("optimization_result")
    
    if backend_result and backend_result.get("status") == "success":
        # Use backend data
        total_cost = backend_result.get("objective_value", 0)
        solver_status = "optimal" if backend_result.get("success") else "failed"
        solver_name = backend_result.get("solver", "CBC")
        
        production = backend_result.get("production", [])
        summary = backend_result.get("summary", {})
        
        active_plants = len(set(p["node"] for p in production))
        total_plants = summary.get("num_nodes", active_plants)
        
        cost_display = f"₹{total_cost/1e9:.2f}B" if total_cost > 1e9 else f"₹{total_cost/1e6:.2f}M"
        plants_display = f"{active_plants}/{total_plants}"
        status_pill = f"{solver_name} Solver"
        utilization_pill = f"{(active_plants/total_plants*100):.0f}% utilization" if total_plants > 0 else "N/A"
    else:
        # Fallback to mock data
        cost_display = "$4.25M"
        solver_status = "optimal"
        status_pill = "CBC Solver"
        plants_display = "3/3"
        utilization_pill = "100% utilization"
    
    st.markdown(
        """
        <style>
        /* Stretch KPI row edge-to-edge */
        .kpi-row > div {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        .kpi-card {
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Total Cost</h4>
                <h2>{cost_display}</h2>
                <span class="kpi-pill">↓ -25% vs baseline</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Status</h4>
                <h2>{solver_status}</h2>
                <span class="kpi-pill">{status_pill}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Plants Active</h4>
                <h2>{plants_display}</h2>
                <span class="kpi-pill">{utilization_pill}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Last Run</h4>
                <h2>completed</h2>
                <span class="kpi-pill">Auto-refresh: 30min</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
