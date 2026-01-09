import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_network_flow_tab():
    """Display Network Flow tab content"""
    st.subheader("Network Flow Visualization")
    st.caption("Clinker transportation routes and volumes")

    # Real transport plan data from optimization output
    # Format: (source, target, mode, period, trips, qty, cost)
    transport_data = [
        ('IU_015', 'GU_007', 'T2', 1, 13, 39000.00, 17343.30),
        ('IU_003', 'GU_008', 'T2', 1, 8, 24000.00, 8543.77),
        ('IU_015', 'GU_003', 'T2', 1, 14, 42000.00, 22667.96),
        ('IU_010', 'GU_002', 'T2', 1, 3, 9000.00, 6904.76),
        ('IU_020', 'GU_016', 'T2', 1, 23, 69000.00, 11121.88),
        ('IU_020', 'GU_016', 'T2', 2, 32, 96000.00, 15473.92),
        ('IU_015', 'GU_019', 'T2', 1, 8, 24000.00, 11494.40),
        ('IU_015', 'GU_018', 'T2', 1, 7, 21000.00, 9816.31),
        ('IU_010', 'GU_022', 'T2', 1, 5, 15000.00, 7701.30),
        ('IU_010', 'GU_022', 'T2', 2, 1, 3000.00, 1540.26),
        ('IU_009', 'GU_015', 'T1', 1, 94677, 94677.00, 82471241.16),
        ('IU_009', 'GU_015', 'T1', 2, 86233, 86233.00, 75115841.64),
        ('IU_003', 'GU_009', 'T2', 1, 18, 54000.00, 25906.50),
        ('IU_004', 'GU_016', 'T2', 1, 2, 6000.00, 3124.72),
        ('IU_003', 'GU_002', 'T2', 1, 11, 33000.00, 6701.08),
        ('IU_013', 'GU_007', 'T2', 1, 10, 30000.00, 17447.50),
        ('IU_013', 'GU_007', 'T2', 2, 2, 6000.00, 3489.50),
        ('IU_020', 'GU_013', 'T2', 1, 9, 27000.00, 6569.64),
        ('IU_020', 'GU_013', 'T2', 2, 9, 27000.00, 6569.64),
        ('IU_002', 'GU_021', 'T2', 1, 10, 30000.00, 13151.90),
        ('IU_011', 'GU_002', 'T2', 1, 6, 18000.00, 4672.32),
        ('IU_011', 'GU_002', 'T2', 2, 17, 51000.00, 13238.24),
        ('IU_013', 'GU_018', 'T2', 1, 7, 21000.00, 10416.00),
        ('IU_013', 'GU_018', 'T2', 2, 9, 27000.00, 13392.00),
        ('IU_007', 'GU_019', 'T1', 1, 70729, 70729.00, 95322887.88),
        ('IU_007', 'GU_019', 'T1', 2, 51069, 51069.00, 68826712.68),
        ('IU_009', 'GU_001', 'T1', 1, 141200, 141200.00, 153241536.00),
        ('IU_009', 'GU_001', 'T1', 2, 124345, 124345.00, 134949141.60),
        ('IU_006', 'GU_013', 'T2', 2, 9, 27000.00, 4877.46),
        ('IU_016', 'GU_006', 'T2', 1, 13, 39000.00, 11856.00),
        ('IU_004', 'GU_013', 'T2', 1, 9, 27000.00, 2568.24),
        ('IU_004', 'GU_013', 'T2', 2, 1, 3000.00, 285.36),
        ('IU_010', 'GU_012', 'T2', 1, 24, 72000.00, 18754.56),
        ('IU_010', 'GU_012', 'T2', 2, 19, 57000.00, 14847.36),
        ('IU_002', 'GU_009', 'T2', 1, 18, 54000.00, 20645.28),
        ('IU_007', 'GU_003', 'T1', 1, 36610, 36610.00, 61275987.50),
        ('IU_007', 'GU_015', 'T1', 1, 94677, 94677.00, 134999934.30),
        ('IU_002', 'GU_023', 'T2', 1, 17, 51000.00, 12011.86),
        ('IU_013', 'GU_006', 'T2', 1, 19, 57000.00, 22163.50),
        ('IU_013', 'GU_006', 'T2', 2, 23, 69000.00, 26829.50),
        ('IU_017', 'GU_007', 'T2', 1, 2567, 2567.00, 3421708.32),
        ('IU_017', 'GU_007', 'T2', 2, 23985, 23985.00, 31971045.60),
        ('IU_008', 'GU_010', 'T2', 2, 6, 18000.00, 5079.06),
        ('IU_010', 'GU_013', 'T2', 1, 9, 27000.00, 9650.07),
        ('IU_010', 'GU_013', 'T2', 2, 9, 27000.00, 9650.07),
        ('IU_010', 'IU_011', 'T2', 1, 25, 75000.00, 32577.50),
        ('IU_019', 'GU_016', 'T2', 1, 19, 57000.00, 13552.32),
        ('IU_013', 'GU_023', 'T2', 1, 17, 51000.00, 16524.00),
        ('IU_013', 'GU_023', 'T2', 2, 14, 42000.00, 13608.00),
        ('IU_002', 'GU_020', 'T2', 1, 8, 24000.00, 11437.95),
        ('IU_006', 'GU_014', 'T2', 2, 6, 18000.00, 7285.14),
        ('IU_004', 'GU_012', 'T2', 1, 24, 72000.00, 12024.00),
        ('IU_008', 'GU_002', 'T2', 1, 11, 33000.00, 13480.50),
        ('IU_008', 'GU_002', 'T2', 2, 11, 33000.00, 13480.50),
        ('IU_009', 'GU_019', 'T1', 1, 57145, 57145.00, 73872484.40),
        ('IU_005', 'GU_008', 'T2', 1, 4, 12000.00, 5397.93),
        ('IU_005', 'GU_008', 'T2', 2, 11, 33000.00, 14844.30),
        ('IU_005', 'GU_010', 'T2', 1, 17, 51000.00, 15409.82),
        ('IU_005', 'GU_010', 'T2', 2, 6, 18000.00, 5438.76),
        ('IU_017', 'GU_024', 'T2', 2, 24764, 24764.00, 40786308.00),
        ('IU_019', 'GU_013', 'T2', 1, 9, 27000.00, 6233.76),
    ]

    # Selector for IU node with search feature
    all_ius = sorted(set([t[0] for t in transport_data]))
    
    # Create search and dropdown in columns
    col_search, col_dropdown = st.columns([0.8, 1.2])
    
    with col_search:
        search_text = st.text_input("Search IU", placeholder="e.g., IU_001", label_visibility="collapsed")
    
    # Filter IUs based on search
    if search_text:
        filtered_ius = [iu for iu in all_ius if search_text.upper() in iu.upper()]
        if not filtered_ius:
            filtered_ius = ["All"]
    else:
        filtered_ius = all_ius
    
    with col_dropdown:
        choice = st.selectbox("Production Node", ["All"] + filtered_ius, index=0, label_visibility="collapsed")

    # Filter data if a specific IU is chosen
    if choice != "All":
        filtered_data = [t for t in transport_data if t[0] == choice]
    else:
        filtered_data = transport_data

    if not filtered_data:
        st.warning("No flows for the selected production node.")
        return
    
    # Aggregate flows by source->target (sum trips/qty/cost across all periods/modes)
    flow_dict = {}
    for source, target, mode, period, trips, qty, cost in filtered_data:
        key = (source, target)
        if key not in flow_dict:
            flow_dict[key] = {'trips': 0, 'qty': 0, 'cost': 0}
        flow_dict[key]['trips'] += trips
        flow_dict[key]['qty'] += qty
        flow_dict[key]['cost'] += cost
    
    sources = [k[0] for k in flow_dict.keys()]
    targets = [k[1] for k in flow_dict.keys()]
    values = [flow['qty'] for flow in flow_dict.values()]
    
    # Create node labels
    all_nodes = list(dict.fromkeys(sources + targets))
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Map to indices
    source_indices = [node_dict[s] for s in sources]
    target_indices = [node_dict[t] for t in targets]
    
    # Color nodes: IU (plants) are darker, GU (warehouses) are lighter
    node_colors = []
    for node in all_nodes:
        if node.startswith('IU'):
            node_colors.append('#5A7863')  # Dark green for IU
        else:
            node_colors.append('#90AB8B')  # Light green for GU
    
    # Scale link thickness down so ribbons appear thinner while keeping original volumes in hover
    value_scale = 0.25
    scaled_values = [v * value_scale for v in values]

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=28,
            thickness=12,
            line=dict(color="white", width=2),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=scaled_values,
            customdata=values,
            color='rgba(90, 120, 99, 0.32)',
            hovertemplate='%{source.label} → %{target.label}<br>Volume: %{customdata} trips<extra></extra>'
        )
    )])
    
    fig_sankey.update_layout(
        height=420,
        margin=dict(t=30, b=30, l=10, r=10),
        font=dict(size=13, color='#1F3D2B', family="Arial, sans-serif"),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # Data table
    st.markdown("### Flow Details")

    # Create the DataFrame with actual transport data
    df_flow = pd.DataFrame({
        'Source': sources,
        'Target': targets,
        'Qty (MT)': [flow['qty'] for flow in flow_dict.values()],
        'Trips': [flow['trips'] for flow in flow_dict.values()],
        'Cost (₹)': [flow['cost'] for flow in flow_dict.values()]
    })
    
    # Format columns with thousand separators
    df_flow['Qty (MT)'] = df_flow['Qty (MT)'].apply(lambda x: f"{int(x):,}")
    df_flow['Trips'] = df_flow['Trips'].apply(lambda x: f"{int(x):,}")
    df_flow['Cost (₹)'] = df_flow['Cost (₹)'].apply(lambda x: f"{int(x):,}")

    # Enhanced styling for the DataFrame
    styled_df = (
        df_flow.style
        .set_properties(**{
            'color': '#1F3D2B',
            'border': '1px solid #E0E6E2',
            'padding': '12px',
            'font-size': '14px',
            'text-align': 'center'
        })
        .set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#2d5f3f'),
                    ('color', '#FFFFFF'),
                    ('font-weight', '700'),
                    ('font-size', '13px'),
                    ('border', '1px solid #1f4529'),
                    ('padding', '14px'),
                    ('text-align', 'center'),
                    ('letter-spacing', '0.5px')
                ]
            },
            {
                'selector': 'td',
                'props': [
                    ('padding', '12px 14px'),
                    ('background-color', '#f9faf9'),
                    ('border-bottom', '1px solid #E0E6E2'),
                ]
            },
            {
                'selector': 'tr:nth-child(even)',
                'props': [
                    ('background-color', '#f0f4f2'),
                ]
            },
            {
                'selector': 'tr:hover',
                'props': [
                    ('background-color', '#e8f0eb'),
                    ('box-shadow', '0 2px 4px rgba(31, 69, 41, 0.1)')
                ]
            }
        ])
    )

    st.table(styled_df)
