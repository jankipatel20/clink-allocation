import streamlit as st
import plotly.io as pio
import os

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Clinker Allocation & Optimization",
        layout="wide",
        page_icon="📦"
    )

def setup_plotly_theme():
    """Configure Plotly theme"""
    pio.templates["custom_dark"] = pio.templates["plotly_dark"]
    pio.templates["custom_dark"].layout.paper_bgcolor = "#1e293b"
    pio.templates["custom_dark"].layout.plot_bgcolor = "#1e293b"
    pio.templates["custom_dark"].layout.font.color = "#f8fafc"
    pio.templates.default = "custom_dark"

def load_css(css_file):
    """Load CSS from external file"""
    with open(css_file, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def apply_styles():
    """Load and apply CSS styles"""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    load_css(css_path)
