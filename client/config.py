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
    pio.templates["custom_light"] = pio.templates["plotly_white"]
    pio.templates["custom_light"].layout.legend.font.color = "#1F3D2B"
    pio.templates["custom_light"].layout.font.color = "#1a1a1a"
    pio.templates.default = "custom_light"

def load_css(css_file):
    """Load CSS from external file"""
    with open(css_file, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def apply_styles():
    """Load and apply CSS styles"""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    load_css(css_path)
