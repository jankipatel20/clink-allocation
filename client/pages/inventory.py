import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_inventory_tab():
    """Display Inventory tab content"""
    st.subheader("Inventory Cost Analysis")
    st.caption("Track inventory holding costs across nodes")
    
    # Check if backend data is available
    backend_result = st.session_state.get("optimization_result")
    
    if backend_result and backend_result.get("status") == "success":
        # Use backend data - convert to expected format
        inventory = backend_result.get("inventory", [])
        inventory_data = [
            (i["node"], int(i["period"]), i["quantity"] * 10)  # multiply by 10 for cost proxy
            for i in inventory
        ]
    else:
        # Fallback to mock data
        # Format: (node, period, cost)
        inventory_data = [
        ('IU_002', 1, 245.32),
        ('IU_003', 1, 187.64),
        ('IU_004', 2, 421.78),
        ('IU_005', 1, 156.43),
        ('IU_006', 2, 312.91),
        ('IU_007', 1, 543.27),
        ('IU_008', 1, 289.54),
        ('IU_009', 2, 478.62),
        ('IU_010', 1, 165.81),
        ('IU_011', 2, 334.69),
        ('GU_001', 1, 2134.56),
        ('GU_002', 1, 1876.43),
        ('GU_002', 2, 2341.78),
        ('GU_003', 1, 987.65),
        ('GU_004', 2, 1543.22),
        ('GU_005', 1, 876.34),
        ('GU_006', 1, 3456.78),
        ('GU_007', 2, 2189.43),
        ('GU_008', 1, 1234.56),
        ('GU_009', 1, 876.54),
        ('GU_010', 2, 2341.87),
        ('GU_011', 1, 543.21),
        ('GU_012', 1, 1876.54),
        ('GU_013', 2, 987.43),
    ]
    
    # Get all unique nodes for selector
    all_nodes = sorted(set([row[0] for row in inventory_data]))
    node = st.selectbox("Select Node", all_nodes)
    
    # Filter data for selected node
    node_data = [row for row in inventory_data if row[0] == node]
    
    if not node_data:
        st.warning(f"No inventory cost data for {node}")
        return
    
    # Extract periods and costs
    periods = [row[1] for row in node_data]
    costs = [row[2] for row in node_data]
    
    # Calculate metrics
    total_unmet = sum(costs)
    avg_unmet = total_unmet / len(costs) if costs else 0
    
    # Line chart
    fig_inv = go.Figure()
    
    fig_inv.add_trace(go.Scatter(
        x=periods,
        y=costs,
        mode='lines+markers',
        name='Inventory Cost',
        line=dict(color='#5A7863', width=3),
        marker=dict(size=10, color='#5A7863'),
        fill='tozeroy',
        fillcolor='rgba(90, 120, 99, 0.2)'
    ))
    
    fig_inv.update_layout(
        height=400,
        hovermode='x unified',
        font=dict(
            color='#1F3D2B',
            size=13,
            family="Inter, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(
                color="#1F3D2B",
                size=12,
            )
        ),
        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='#E7EEEA',
        plot_bgcolor="#E7EEEA",
        xaxis=dict(
            title="Period",
            title_font=dict(color="#1F3D2B", size=14),
            tickfont=dict(color="#1F3D2B", size=12),
            gridcolor='#90AB8B',
            gridwidth=0.5
        ),
        yaxis=dict(
            title="Inventory Cost",
            title_font=dict(color="#1F3D2B", size=14),
            tickfont=dict(color="#1F3D2B", size=12),
            gridcolor='#90AB8B',
            gridwidth=0.5,
            rangemode="tozero"
        )
    )

    st.plotly_chart(fig_inv, use_container_width=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", f"₹{total_unmet:,.2f}")
    with col2:
        st.metric("Average per Period", f"₹{avg_unmet:,.2f}")
    with col3:
        st.metric("Periods", len(periods))
