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
    nav_left, nav_right = st.columns([3, 2])
    
    with nav_left:
        st.markdown(
            '<div class="nav-left">Clinker Allocation & Optimization</div>',
            unsafe_allow_html=True
        )
    
    return nav_right
