import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_network_flow_tab():
    """Display Network Flow tab content"""
    st.subheader("Network Flow Visualization")
    st.caption("Clinker transportation routes and volumes")

    # Base data
    sources = ['Plant A', 'Plant A', 'Plant B', 'Plant B', 'Plant C', 'Warehouse North', 'Warehouse South']
    targets = ['Warehouse North', 'Warehouse South', 'Warehouse North', 'Customer East', 'Warehouse South', 'Customer East', 'Customer West']
    values = [3500, 2000, 4500, 3000, 4000, 2000, 3500]
    costs = [175, 120, 225, 180, 200, 60, 105]

    # Selector for Production (IU) node
    plants = sorted({s for s in sources if 'Plant' in s})
    choice = st.selectbox("Select production node (IU)", ["All"] + plants, index=0)

    # Filter data if a specific plant is chosen
    if choice != "All":
        mask = [s == choice for s in sources]
        filtered_sources = [s for s, m in zip(sources, mask) if m]
        filtered_targets = [t for t, m in zip(targets, mask) if m]
        filtered_values = [v for v, m in zip(values, mask) if m]
        filtered_costs = [c for c, m in zip(costs, mask) if m]
    else:
        filtered_sources, filtered_targets, filtered_values, filtered_costs = sources, targets, values, costs

    if not filtered_sources:
        st.warning("No flows for the selected production node.")
        return
    
    # Create node labels
    all_nodes = list(dict.fromkeys(filtered_sources + filtered_targets))
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Map to indices
    source_indices = [node_dict[s] for s in filtered_sources]
    target_indices = [node_dict[t] for t in filtered_targets]
    
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
            pad=32,  # more spacing between columns for clearer separation
            thickness=15,
            line=dict(color="white", width=2),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=filtered_values,
            color='rgba(90, 120, 99, 0.3)',
            hovertemplate='%{source.label} → %{target.label}<br>Volume: %{value} tons<extra></extra>'
        )
    )])
    
    fig_sankey.update_layout(
        height=450,
        width=720,  # narrower overall width
        margin=dict(t=30, b=30, l=20, r=20),
        font=dict(size=13, color='#1F3D2B', family="Arial, sans-serif"),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    
    st.plotly_chart(fig_sankey, use_container_width=False)
    
    # Data table
    st.markdown("### Flow Details")

    # Create the DataFrame
    df_flow = pd.DataFrame({
        'Source': filtered_sources,
        'Target': filtered_targets,
        'Volume (tons)': filtered_values,
        'Cost ($)': [f'${c:,}' for c in filtered_costs]
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
