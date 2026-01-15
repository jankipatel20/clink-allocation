import streamlit as st

def display_navbar():
    """Display the top navigation bar"""
    st.markdown("""
    <div class="navbar">
        <div class="nav-left"> Clinker Allocation & Optimization</div>
    </div>
    """, unsafe_allow_html=True)

def display_section_nav():
    """Display the middle section navigation with logo"""
    _, nav_right = st.columns([3, 2])
    return nav_right
