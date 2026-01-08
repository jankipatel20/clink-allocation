import streamlit as st

# Import configuration
from config import setup_page, setup_plotly_theme, apply_styles

# Import components
from components.navbar import display_navbar, display_section_nav
from components.kpi_cards import display_kpi_cards
from components.file_uploader import display_uploader_and_button, handle_optimization
from components.footer import display_footer
from components.floating_whatsapp import display_floating_whatsapp

# Import pages
from pages.overview import display_overview_tab
from pages.network_flow import display_network_flow_tab
from pages.inventory import display_inventory_tab
from pages.scenarios import display_scenarios_tab

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

# ===== Navigation Section =====
nav_right = display_section_nav()
optimize_clicked = display_uploader_and_button(nav_right)

if optimize_clicked:
    handle_optimization()

# ===== Tabs =====
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Network Flow", "Inventory", "Scenarios"])

with tab1:
    display_overview_tab()

with tab2:
    display_network_flow_tab()

with tab3:
    display_inventory_tab()

with tab4:
    display_scenarios_tab()

# ===== Footer =====
display_footer()

# ===== Floating WhatsApp Button =====
display_floating_whatsapp()
