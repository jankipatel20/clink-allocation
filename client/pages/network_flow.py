import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_network_flow_tab():
    """Display Network Flow tab content"""
    st.subheader("Network Flow Visualization")
    st.caption("Clinker transportation routes and volumes")
    
    # Sankey diagram
    sources = ['Plant A', 'Plant A', 'Plant B', 'Plant B', 'Plant C', 'Warehouse North', 'Warehouse South']
    targets = ['Warehouse North', 'Warehouse South', 'Warehouse North', 'Customer East', 'Warehouse South', 'Customer East', 'Customer West']
    values = [3500, 2000, 4500, 3000, 4000, 2000, 3500]
    costs = [175, 120, 225, 180, 200, 60, 105]
    
    # Create node labels
    all_nodes = list(set(sources + targets))
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Map to indices
    source_indices = [node_dict[s] for s in sources]
    target_indices = [node_dict[t] for t in targets]
    
    # Color nodes
    node_colors = []
    for node in all_nodes:
        if 'Plant' in node:
            node_colors.append('#5A7863')
        elif 'Warehouse' in node:
            node_colors.append('#90AB8B')
        else:
            node_colors.append('#3B4953')
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=15,
            line=dict(color="white", width=2),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(90, 120, 99, 0.3)',
            hovertemplate='%{source.label} → %{target.label}<br>Volume: %{value} tons<extra></extra>'
        )
    )])
    
    fig_sankey.update_layout(
        height=450,
        margin=dict(t=30, b=30, l=30, r=30),
        font=dict(size=13, color='#1F3D2B', family="Arial, sans-serif"),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # Data table
    st.markdown("### Flow Details")

    # Create the DataFrame
    df_flow = pd.DataFrame({
        'Source': sources,
        'Target': targets,
        'Volume (tons)': values,
        'Cost ($)': [f'${c:,}' for c in costs]
    })

    # Style the DataFrame
    styled_df = (
        df_flow.style
        .set_properties(**{
            'background-color': '#FFFFFF',
            'color': '#1F3D2B',
            'border-color': '#D6E0D8'
        })
        .set_table_styles(
            [{
                'selector': 'th',
                'props': [
                    ('background-color', '#1F3D2B'),
                    ('color', '#FFFFFF'),
                    ('font-weight', 'bold')
                ]
            }]
        )
    )

    st.table(styled_df)
