import streamlit as st
import plotly.graph_objects as go

def display_inventory_tab():
    """Display Inventory tab content"""
    st.subheader("Inventory vs Safety Stock")
    st.caption("Track inventory levels against safety stock thresholds")
    
    # Plant selector
    plant = st.selectbox("Select Plant", ["Plant A", "Plant B", "Plant C"])
    
    # Generate data
    periods = [1, 2, 3, 4]
    
    if plant == "Plant A":
        inventory = [2600, 2800, 2300, 2650]
        avg_inventory = 2550
    elif plant == "Plant B":
        inventory = [2200, 2500, 2100, 2400]
        avg_inventory = 2300
    else:
        inventory = [1900, 2200, 1800, 2100]
        avg_inventory = 2000
    
    safety_stock = [1000] * 4
    
    # Line chart
    fig_inv = go.Figure()
    
    fig_inv.add_trace(go.Scatter(
        x=periods,
        y=inventory,
        mode='lines+markers',
        name='Current Inventory',
        line=dict(color='#5A7863', width=3),
        marker=dict(size=10)
    ))
    
    fig_inv.add_trace(go.Scatter(
        x=periods,
        y=safety_stock,
        mode='lines',
        name='Safety Stock',
        line=dict(color='#3B4953', width=2, dash='dash')
    ))
    
    fig_inv.update_layout(
        height=400,
        hovermode='x unified',
        font=dict(
            color='#1F3D2B',
            size=13,
            family="Arial, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(
                color="#1F3D2B",
                size=12,
                weight="bold"
            )
        ),
        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='#E7EEEA',
        plot_bgcolor="#E7EEEA",
        xaxis=dict(
            title="Period",
            title_font=dict(color="#1F3D2B", size=14, weight="bold"),
            tickfont=dict(color="#1F3D2B", size=12),
            gridcolor='#90AB8B',
            gridwidth=0.5
        ),
        yaxis=dict(
            title="Inventory (tons)",
            title_font=dict(color="#1F3D2B", size=14, weight="bold"),
            tickfont=dict(color="#1F3D2B", size=12),
            gridcolor='#90AB8B',
            gridwidth=0.5,
            rangemode="tozero"
        )
    )

    st.plotly_chart(fig_inv, use_container_width=True)
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Inventory", f"{avg_inventory:,} tons")
    with col2:
        st.metric("Safety Stock", "1,000 tons")
