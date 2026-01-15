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
            background-color: #f8f9fa;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            border: 1px solid #d1d5db;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-right: 0 !important;
            display: flex;
            align-items: center;
        }

        /* 3. Text Color (Green) */
        div[role="radiogroup"] label p {
            color: #1F3D2B !important; 
            font-weight: 600;
            font-size: 1rem;
            margin: 0;
        }

        /* 4. RESET THE RADIO BUTTON (The Fix) */
        div[role="radiogroup"] input[type="radio"] {
            /* This forcefully hides the default Red/Black dot */
            -webkit-appearance: none !important; 
            -moz-appearance: none !important;
            appearance: none !important;
            
            /* Define our own shape */
            width: 18px !important;
            height: 18px !important;
            border-radius: 50% !important;
            outline: none !important;
            margin-right: 10px;
            cursor: pointer;
            
            /* Default State (Unchecked) - Grey Ring */
            background-color: transparent !important;
            border: 2px solid #9ca3af !important;
        }

        /* 5. ACTIVE STATE (Checked) - Green Dot */
        div[role="radiogroup"] input[type="radio"]:checked {
            /* Turn the circle Green */
            background-color: #2d5f3f !important; 
            border-color: #2d5f3f !important;
            
            /* This 'inset shadow' creates the white gap inside the green circle */
            box-shadow: inset 0 0 0 3px white !important; 
        }

        /* 6. Active Box Styling */
        div[role="radiogroup"] label:has(input:checked) {
            background-color: #e8f5e9 !important;
            border-color: #2d5f3f !important;
        }
        
        /* 7. Hover Effects */
        div[role="radiogroup"] label:hover {
            border-color: #2d5f3f;
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