import streamlit as st

def display_kpi_cards():
    """Display KPI cards row"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Total Cost</h4>
                <h2>$4.25M</h2>
                <span class="kpi-pill">↓ -25% vs baseline</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Status</h4>
                <h2>optimal</h2>
                <span class="kpi-pill">CBC Solver</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-left">
                <h4>Plants Active</h4>
                <h2>3/3</h2>
                <span class="kpi-pill">100% utilization</span>
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
