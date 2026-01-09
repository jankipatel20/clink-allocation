import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_overview_tab():
    """Display Overview tab content"""
    st.subheader("Cost Breakdown")
    st.caption("Distribution of optimization costs")
    
    # Check if history should be shown (controlled by button in file_uploader)
    # Use direct access to ensure we get the latest state value
    show_history = st.session_state.get("show_history", False)
    
    if show_history:
        col_chart, col_history = st.columns([1.2, 0.8])
        with col_chart:
            display_cost_breakdown()
        with col_history:
            display_history_panel()
    else:
        display_cost_breakdown()

def display_cost_breakdown():
    """Display cost breakdown pie chart and cards"""
    
    # Real data from latest optimization output
    total_production_cost = 20285344588.41
    total_inventory_cost = 566891.57
    total_transport_cost = 956895249.57
    total_cost = total_production_cost + total_inventory_cost + total_transport_cost
    
    costs = {
        'Production Cost': total_production_cost,
        'Transportation Cost': total_transport_cost,
        'Inventory Cost': total_inventory_cost
    }
    
    colors = ['#5A7863', '#3B4953', "#90AB8B"]
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(costs.keys()),
        values=list(costs.values()),
        hole=0.4,
        marker=dict(colors=colors),
        textposition='auto',
        textinfo='label+percent'
    )])
    
    fig_pie.update_layout(
        showlegend=True,
        height=360,
        margin=dict(t=12, b=12, l=12, r=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#1F3D2B",
                size=12,
                family="Arial, sans-serif"
            )
        ),
        font=dict(
            color="#1F3D2B",
            size=12,
            family="Arial, sans-serif"
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Format costs for display
    prod_cost = total_production_cost / 1e9
    trans_cost = total_transport_cost / 1e9
    inv_cost = total_inventory_cost / 1e6
    
    # Cost boxes
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="cost-card">
            <div class="cost-title">Production</div>
            <div class="cost-value">₹{prod_cost:.2f}B</div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="cost-card">
            <div class="cost-title">Transportation</div>
            <div class="cost-value">₹{trans_cost:.2f}B</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
        <div class="cost-card">
            <div class="cost-title">Inventory</div>
            <div class="cost-value">₹{inv_cost:.2f}M</div>
        </div>
        """, unsafe_allow_html=True)


def display_history_panel():
    """Display optimization history panel with previous runs"""
    st.subheader("Optimization History")
    st.caption("Previous run results")
    
    # Mock history data with varied costs and scenarios
    history_data = {
        'Run #': ['#5', '#4', '#3', '#2', '#1'],
        'Date': ['2024-01-08 14:32', '2024-01-08 11:15', '2024-01-07 16:45', '2024-01-07 09:20', '2024-01-06 13:10'],
        'Total': ['$4.25M', '$4.85M', '$3.95M', '$5.20M', '$4.50M'],
        'Prod': ['$2.50M', '$2.80M', '$2.35M', '$3.10M', '$2.65M'],
        'Inv': ['$0.75M', '$1.05M', '$0.60M', '$1.20M', '$0.90M'],
        'Trans': ['$1.00M', '$1.00M', '$1.00M', '$0.90M', '$0.95M'],
        'Status': ['Optimal', 'Feasible', 'Optimal', ' Feasible', 'Optimal']
    }
    
    df_history = pd.DataFrame(history_data)
    
    # Display as styled table
    styled_df = (
        df_history.style
        .set_properties(**{
            'background-color': '#FFFFFF',
            'color': '#1F3D2B',
            'border-color': '#D6E0D8',
            'font-size': '11px',
            'text-align': 'center'
        })
        .set_table_styles(
            [{
                'selector': 'th',
                'props': [
                    ('background-color', '#1F3D2B'),
                    ('color', '#FFFFFF'),
                    ('font-weight', 'bold'),
                    ('font-size', '11px'),
                    ('text-align', 'center')
                ]
            }]
        )
    )
    
    st.table(styled_df)
    
    # Summary stats
    st.markdown("### Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Runs", "5", "Latest")
    with col2:
        st.metric("Best Cost", "$3.95M", "↓ 7.1%")
    with col3:
        st.metric("Avg Cost", "$4.55M", "")

