import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.io as pio

pio.templates["custom_light"] = pio.templates["plotly_white"]
pio.templates["custom_light"].layout.legend.font.color = "#1F3D2B"
pio.templates["custom_light"].layout.font.color = "#1a1a1a"
pio.templates.default = "custom_light"

# Page configuration
st.set_page_config(page_title="Clinker Allocation & Optimization", layout="wide", page_icon="📦")

st.markdown("""
<div class="navbar">
    <div class="nav-left"> Clinker Allocation & Optimization</div>
</div>
""", unsafe_allow_html=True)

# Custom CSS for Light Mode
st.markdown("""
<style>
h3 {
    color: #1F3D2B !important;   /* dark green */
    font-weight: 700;
}
[data-testid="stMainBlockContainer"]{
    margin: 0; 
    padding: 5rem 2rem 2rem 2rem;      
    }
/* ===== App Background ===== */
.stApp {
    background-color: #F4F7F2;
}
/* Subheaders */
[data-testid="stSubheader"] {
    color: #1F3D2B !important;
    font-weight: 700 !important;
}

/* Captions */
[data-testid="stCaptionContainer"] {
    color: #1F3D2B !important;
    font-weight: 700 !important;
}
/* ===== Global Card Styling ===== */
.block-container,
[data-testid="stMetric"],
[data-testid="stContainer"],
[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #D6E0D8;
    box-shadow: 0 6px 18px rgba(31, 61, 43, 0.12);
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 12px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #FFFFFF;
    border: 1px solid #D6E0D8;
    border-radius: 12px;
    padding: 12px 22px;
    color: #1F3D2B;
    box-shadow: 0 4px 12px rgba(31,61,43,0.1);
}
.stTabs [aria-selected="true"] {
    background-color: #1F3D2B !important;
    color: #FFFFFF !important;
}

/* ===== Buttons ===== */
.stButton > button {
    background-color: #FFFFFF;
    color: #1F3D2B;
    border: 1px solid #1F3D2B;
    border-radius: 10px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(31,61,43,0.15);
}
.stButton > button[kind="primary"] {
    background-color: #1F3D2B;
    color: #FFFFFF;
}
.stButton > button:hover {
    transform: translateY(-1px);
}

/* ===== Text ===== */
h1, h2, h3 {
    color: #1F3D2B !important;
}
.stCaption {
    color: #23451D !important;
    font-weight: 500;
}
/* ===== Gap ===== */

.stElementContainer {
            box-shadow: 20 6px 20px rgba(31,61,43,0.12);
            bgcolor: #DCFCE7;
        }
/* ===== Navbar ===== */
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(31,61,43,0.85);
    padding: 10px 18px;
    border-bottom: 1px solid #D6E0D8;
    border-radius:10px;
    box-shadow: 0 6px 20px rgba(31,61,43,0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-left {
    font-size: 26px;
    font-weight: 600;
    color: white;
}

/* Style Streamlit button */
div.stButton > button {
    background: #1F3D2B;
    color: white;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 16px;
    border: none;
}

div.stButton > button:hover {
    background: #3e8e41;
}

/* Style File Uploader to look like a button */
[data-testid="stFileUploader"] {
    width: auto;
    padding: 0;
}

[data-testid="stFileUploader"] > label {
    display: none !important;
}

[data-testid="stFileUploader"] section {
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
}

/* Hide drag-and-drop text, dropzone, and status */
[data-testid="stFileUploader"] section > div:nth-child(1),
[data-testid="stFileUploader"] section > div:nth-child(2),
[data-testid="stFileUploader"] section + div {
    display: none !important;
}

/* Hide any remaining helper text inside the section */
[data-testid="stFileUploader"] section div {
    display: none !important;
}

/* Hide native input but keep it functional */
[data-testid="stFileUploader"] input[type="file"] {
    opacity: 0;
    height: 0;
    width: 0;
    position: absolute;
}

/* Style the visible button */
[data-testid="stFileUploader"] button {
    background: #1F3D2B;
    color: white;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 16px;
    border: none;
    width: 100%;
}

[data-testid="stFileUploader"] button svg,
[data-testid="stFileUploader"] button p,
[data-testid="stFileUploader"] button div,
            # !
[data-testid="stFileUploader"] button span {
    display: none;
}

[data-testid="stFileUploader"] button::after {
}

[data-testid="stFileUploader"] button:hover {
    background: #3e8e41;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* 1. The Metric Container (Card) */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #D6E0D8;   /* Light green/grey border */
    border-radius: 12px;         /* Rounded corners */
    padding: 20px 24px;          /* Proper internal padding */
    width: 100%;                 /* Full width of column */
    box-shadow: none !important; /* Flat design (as requested previously) */
    transition: all 0.2s ease;   /* Smooth hover effect */
}

/* Optional: Slight border darken on hover */
[data-testid="stMetric"]:hover {
    border-color: #1F3D2B;
}

/* 2. The Label (Top text like "Total Cost") */
[data-testid="stMetricLabel"] {
    color: #5A7863 !important;   /* Medium Green */
    font-size: 14px !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important; /* Spacing between label and value */
}

/* 3. The Value (The big number) */
[data-testid="stMetricValue"] {
    color: #1F3D2B !important;   /* Dark Forest Green */
    font-size: 28px !important;  /* Make it big */
    font-weight: 800 !important; /* Extra Bold */
    font-family: 'Arial', sans-serif;
}

/* 4. The Delta (The change indicator) */
[data-testid="stMetricDelta"] {
    font-weight: 600;
    font-size: 14px;
    margin-top: 6px;             /* Spacing from value */
}

/* 5. Center align everything (Optional - Remove if you prefer left align) */
[data-testid="stMetric"] > div {
    display: flex;
    flex-direction: column;
    align-items: flex-start; /* 'center' for centered, 'flex-start' for left */
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSubheader"] {
    color: #1F3D2B !important;
    font-weight: 700 !important;
}

[data-testid="stCaptionContainer"] {
    color: #1F3D2B !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.cost-card {
    background: #FFFFFF;
    border: 1px solid #D6E0D8;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(31,61,43,0.14);
}
.cost-title {
    color: #1F3D2B;
    font-weight: 700;
    font-size: 16px;
}
.cost-value {
    color: #1F3D2B;
    font-size: 22px;
    font-weight: 800;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.kpi-card {
    background: #ffffff;
    border-radius: 16px;
    height: 140px;
    width:300px;
    padding: 10px 10px 10px 10px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    border: 1px solid #E5E7EB;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.kpi-left h4 {
    margin: 0;
    padding: 0;
    font-size: 14px;
    color: #475569;
    font-weight: 600;
}

.kpi-left h2 {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    font-size: 25px;
    font-weight: 800;
    padding: 0 0 4px 0 ;
    color: #0F172A;
}

.kpi-pill {
    display: inline-block;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 999px;
    background: #DCFCE7;
    color: #16A34A;
}

.kpi-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.blue { background:#DBEAFE; color:#2563EB; }
.green { background:#DCFCE7; color:#16A34A; }
.purple { background:#F3E8FF; color:#7C3AED; }
.yellow { background:#FEF3C7; color:#D97706; }
            
.stAlertContainer {
            background-color: #DCFCE7 !important;
            color: #1F3D2B !important;
            border-radius: 8px !important;
            }
.stColumn {
        box-shadow: 20 6px 20px rgba(31,61,43,0.12);
        bgcolor: #DCFCE7;
        }
.stVerticalBlock{
    gap: .5rem;
    box-shadow: 20 6px 20px rgba(31,61,43,0.12);
    bgcolor: #DCFCE7;
    color: #1F3D2B !important;
}
.stElementContainer {
            box-shadow: 20 6px 20px rgba(31,61,43,0.12);
            bgcolor: #DCFCE7;
        }

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
            
.footer-container {
    padding: 20px;
    background: white;
    border-radius: 12px;
    border: 1px solid #ddd;
}
.footer-title {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 18px;
    color: #0f172a;
}
.footer-section {
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
}
.footer-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 36px;
}
</style>
""", unsafe_allow_html=True)

# Metrics Row
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

st.markdown("---")

nav_left, nav_right = st.columns([3, 2])

with nav_left:
    st.markdown(
        '<div class="nav-left">Clinker Allocation & Optimization</div>',
        unsafe_allow_html=True
    )

with nav_right:
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        uploaded_file = st.file_uploader(
            "",
            type=["csv"],
            help="Upload CSV data file",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            try:
                uploaded_data = pd.read_csv(uploaded_file)
                st.success(f"✅ {uploaded_file.name} uploaded!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col_btn2:
        optimize_clicked = st.button("Run Optimization", use_container_width=True)

if optimize_clicked:
    st.success("Optimization started!")
    # call your optimization function here
    # run_optimization()


# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Network Flow", "Inventory", "Scenarios"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Cost Breakdown")
        st.caption("Distribution of optimization costs")
        
        # Pie chart data
        costs = {
            'Production Cost': 2.50,
            'Inventory Cost': 0.75,
            'Transport Cost': 1.00
        }
        
        colors = ['#5A7863', "#90AB8B", '#3B4953']
        
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
            height=400,
            margin=dict(t=30, b=30, l=30, r=30),
            # legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            # paper_bgcolor='#ffffff',
            # plot_bgcolor='#ffffff',
            # font=dict(color='#1a1a1a', size=13, family="Arial, sans-serif"),
            legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5,
        font=dict(
            color="#1F3D2B",   # dark green legend text
            size=13,
            family="Arial, sans-serif"
        )
    ),
    font=dict(
        color="#1F3D2B",      # fallback text color
        size=13,
        family="Arial, sans-serif"
    ),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Cost boxes
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("""
            <div class="cost-card">
                <div class="cost-title">Production</div>
                <div class="cost-value">$2.50M</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div class="cost-card">
                <div class="cost-title">Inventory</div>
                <div class="cost-value">$0.75M</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c:
            st.markdown("""
            <div class="cost-card">
                <div class="cost-title">Transport</div>
                <div class="cost-value">$1.20M</div>
            </div>
            """, unsafe_allow_html=True)

    
    with col2:
        st.subheader("Production Utilization Heatmap")
        st.caption("Weekly capacity utilization across plants")
        
        # Heatmap data
        utilization_data = {
            'Plant': ['Plant A', 'Plant B', 'Plant C'],
            'Week 1': [85, 92, 78],
            'Week 2': [88, 95, 81],
            'Week 3': [82, 89, 75],
            'Week 4': [86, 93, 79]
        }
        
        df_heat = pd.DataFrame(utilization_data)
        df_heat_values = df_heat.set_index('Plant').values
        
        # Custom color scale
        colorscale = [
            [0, '#dc3545'],      # red for <60%
            [0.6, '#ffc107'],    # orange for 60-69%
            [0.7, '#ffc107'],    # yellow for 70-79%
            [0.8, '#90AB8B'],    # light green for 80-89%
            [1, '#5A7863']       # green for ≥90%
        ]
        
        fig_heat = go.Figure(data=go.Heatmap(
            z=df_heat_values,
            x=['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            y=df_heat['Plant'],
            text=df_heat_values,
            texttemplate='%{text}%',
            textfont={"size": 14, "color": "#3D5143"},
            colorscale=colorscale,
            showscale=False,
            hovertemplate='Plant: %{y}<br>Week: %{x}<br>Utilization: %{z}%<extra></extra>'
        ))
        
        fig_heat.update_layout(
            height=400,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='#ffffff',
            plot_bgcolor="#D9D9D9",
            font=dict(color='#1a1a1a', size=13, family="Arial, sans-serif"),
            yaxis=dict(
        autorange='reversed',
        tickfont=dict(
            color="#1F3D2B",   # dark green
            size=14,
            family="Arial, sans-serif"
        )
    ),
    xaxis=dict(
        side='top',
        tickfont=dict(
            color="#1F3D2B",
            size=14
        )
    )
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # Legend
        st.markdown("""
<div style="font-weight:600;">
<span style="color:#1F3D2B; font-weight:600;">Utilization:</span><br>
<span style="color:#8B1E1E;"> 🔴 60%</span> |
<span style="color:#C77800;"> 🟠 60–69%</span> |
<span style="color:#C7A600;"> 🟡 70–79%</span> |
<span style="color:#4F7F65;"> 🟢 80–89%</span> |
<span style="color:#1F3D2B;"> 🟢 ≥90%</span>
</div>
""", unsafe_allow_html=True)

with tab2:
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

    # 1. Create the DataFrame
    df_flow = pd.DataFrame({
        'Source': sources,
        'Target': targets,
        'Volume (tons)': values,
        'Cost ($)': [f'${c:,}' for c in costs]
    })

    # 2. Style the DataFrame (Headers + Rows)
    styled_df = (
        df_flow.style
        # Style the data rows (White bg, Green text)
        .set_properties(**{
            'background-color': '#FFFFFF',
            'color': '#1F3D2B',
            'border-color': '#D6E0D8'
        })
        # Style the header row (Dark Green bg, White text)
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

    # 3. Use st.table (This is key: st.table respects header styling)
    st.table(styled_df)

with tab3:
    # --- 1. Custom CSS for the Dropdown Background ---
    # Streamlit selectboxes are hard to style, so we inject specific CSS
    st.markdown("""
        <style>
        /* Change the background of the dropdown input box */
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #1F3D2B !important;
            color: #1F3D2B !important;
            border-radius: 8px;
        }
        /* Change the text color inside the dropdown */
        div[data-baseweb="select"] span {
            color: #1F3D2B !important;
            font-weight: 600;
        }
        /* Change the dropdown arrow color */
        div[data-baseweb="select"] svg {
            fill: #1F3D2B !important;
        }
        
        </style>
    """, unsafe_allow_html=True)

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
    
    # --- 2. Updated Plotly Layout with Custom Colors ---
    fig_inv.update_layout(
        height=400,
        hovermode='x unified',
        
        # Global Font Settings (Affects anything not overridden)
        font=dict(
            color='#1F3D2B',       # Dark Green text globally
            size=13, 
            family="Arial, sans-serif"
        ),

        # Legend Styling
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(
                color="#1F3D2B",   # Dark Green Legend Text
                size=12,
                weight="bold"      # Make it pop
            )
        ),

        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='#E7EEEA',
        plot_bgcolor="#E7EEEA",

        # X-Axis Styling
        xaxis=dict(
            title="Period",
            title_font=dict(color="#1F3D2B", size=14, weight="bold"), # Axis Title Color
            tickfont=dict(color="#1F3D2B", size=12),                  # Tick Label Color
            gridcolor='#90AB8B', 
            gridwidth=0.5
        ),

        # Y-Axis Styling
        yaxis=dict(
            title="Inventory (tons)",
            title_font=dict(color="#1F3D2B", size=14, weight="bold"), # Axis Title Color
            tickfont=dict(color="#1F3D2B", size=12),                  # Tick Label Color
            gridcolor='#90AB8B', 
            gridwidth=0.5,
            rangemode="tozero"
            # range=[0, 4000]
        )
    )

    st.plotly_chart(fig_inv, use_container_width=True)
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Inventory", f"{avg_inventory:,} tons")
    with col2:
        st.metric("Safety Stock", "1,000 tons")

with tab4:
    st.subheader("Scenario Analysis")
    st.caption("Run what-if scenarios to test optimization resilience")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Available Scenarios")
        
        # Scenario buttons
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            demand_up = st.button("▶ Demand +20%", use_container_width=True)
        with col_b:
            demand_down = st.button("▶ Demand -15%", use_container_width=True)
        with col_c:
            fuel_up = st.button("▶ Fuel Cost +15%", use_container_width=True)
        
        st.markdown("---")
                        # Results
        st.markdown("### Results")

        if demand_up or demand_down or fuel_up:
            scenario_name = (
                "Demand +20%" if demand_up
                else "Demand -15%" if demand_down
                else "Fuel Cost +15%"
            )

            new_cost = 5.10 if demand_up else (3.61 if demand_down else 4.89)
            delta = "+20%" if demand_up else ("-15%" if demand_down else "+15%")

            st.success(f"Scenario '{scenario_name}' completed")

            col_x, col_y = st.columns(2)
            with col_x:
                st.metric(
                    label="Baseline",
                    value="$4.25M",
                    delta="Current"
                )
            with col_y:
                st.metric(
                    label="Scenario Result",
                    value=f"${new_cost}M",
                    delta=delta,
                    delta_color="inverse"
                )
        else:
            st.info("**Baseline:** $4.25M (Current)")
            st.caption("Run a scenario to see results")

    
    with col2:
        st.markdown("### Scenario Guidelines")
        st.caption("""
        **Demand Scenarios**
        Test how the system responds to demand fluctuations. 
        Use +20% for peak season and -15% for low season.
        
        **Cost Scenarios**
        Evaluate impact of fuel price changes on transportation 
        costs and overall optimization.
        
        **Capacity Scenarios**
        Analyze effects of plant maintenance or temporary 
        capacity reductions.
        """)

st.markdown("---")

st.markdown("""
<div class="footer-container">
    <div class="footer-title">About This System</div>
    <div class="footer-grid">
    <div class="footer-section">
            <h4>Optimization Engine</h4>
            <p>
                Mixed-Integer Linear Programming (MILP) using
                CBC/GLPK solvers via Pyomo
            </p>
        </div>
    <div class="footer-section">
        <h4>Key Constraints</h4>
        <p>
            Production capacity, inventory balance,
            safety stock, trip capacity, and batch quantities
        </p>
    </div>
     <div class="footer-section">
            <h4>Cost Optimization</h4>
            <p>
                Minimizes total costs across production,
                inventory holding, and transportation
            </p>
    </div>
    </div>  
</div>
""", unsafe_allow_html=True)

