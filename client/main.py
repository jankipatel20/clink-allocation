import streamlit as st

# Import configuration
from config import setup_page, setup_plotly_theme, apply_styles

# Import components
from components.navbar import display_navbar, display_section_nav
from components.kpi_cards import display_kpi_cards
from components.file_uploader import display_uploader_and_button, handle_optimization
from components.footer import display_footer

# Import pages
from pages.overview import display_overview_tab
from pages.network_flow import display_network_flow_tab
from pages.inventory import display_inventory_tab

# ===== Setup =====
setup_page()
setup_plotly_theme()
apply_styles()

# ===== Header =====
display_navbar()

# ===== KPI Cards =====
display_kpi_cards()

# ===== Divider =====
st.markdown("---")

# ===== Tabs + Actions Row =====
col_tabs, col_actions = st.columns([2.2, 2], gap="large")

with col_tabs:
    st.markdown(
        """
        <style>
        /* 1. Container Layout */
        div[role="radiogroup"] {
            display: flex;
            flex-direction: row;
            gap: 10px;
            align-items: center;
        }

        /* 2. Box/Label Styling */
        div[role="radiogroup"] label {
            background-color: #1e293b;
            padding: 0.6rem 1.2rem;
            border-radius: 4px;
            border: 1px solid #334155;
            cursor: pointer;
            margin-right: 0 !important;
            display: flex;
            align-items: center;
        }

        /* 3. Text Color */
        div[role="radiogroup"] label p {
            color: #94a3b8 !important; 
            font-weight: 600;
            font-family: 'Courier New', Courier, monospace;
            font-size: 1rem;
            margin: 0;
            text-transform: uppercase;
        }

        /* 4. RESET THE RADIO BUTTON (The Fix) */
        div[role="radiogroup"] input[type="radio"] {
            -webkit-appearance: none !important; 
            -moz-appearance: none !important;
            appearance: none !important;
            
            width: 14px !important;
            height: 14px !important;
            border-radius: 2px !important; /* square look */
            outline: none !important;
            margin-right: 10px;
            cursor: pointer;
            
            background-color: transparent !important;
            border: 2px solid #475569 !important;
        }

        /* 5. ACTIVE STATE (Checked) - Orange Square */
        div[role="radiogroup"] input[type="radio"]:checked {
            background-color: #f97316 !important; 
            border-color: #ea580c !important;
            box-shadow: inset 0 0 0 2px #1e293b !important; 
        }

        /* 6. Active Box Styling */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #334155 !important;
            border-color: #f97316 !important;
        }
        
        div[role="radiogroup"] label:has(input:checked) p {
            color: #f1f5f9 !important;
        }

        /* 7. Hover Effects */
        div[role="radiogroup"] label:hover {
            border-color: #f97316;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    selected_tab = st.radio(
        "Select view",
        ["Overview", "Network Flow", "Inventory"],
        horizontal=True,
        label_visibility="collapsed",
        key="tab_selector",
    )

with col_actions:
    optimize_clicked = display_uploader_and_button(col_actions)

if optimize_clicked:
    handle_optimization()

# ===== Tabs Content =====
if selected_tab == "Overview":
    display_overview_tab()
elif selected_tab == "Network Flow":
    display_network_flow_tab()
elif selected_tab == "Inventory":
    display_inventory_tab()

# ===== Footer =====
display_footer()