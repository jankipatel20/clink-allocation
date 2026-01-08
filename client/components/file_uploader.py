import streamlit as st
import pandas as pd

def display_uploader_and_button(nav_right_col):
    """Display file uploader and optimization button"""
    # Initialize session state for history
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    
    with nav_right_col:
        # Browse Files, Export CSV, History - in one row
        col_btn1, col_btn2, col_btn3 = st.columns([1.1, 1, 1])
        
        with col_btn1:
            uploaded_files = st.file_uploader(
                "",
                type=["csv"],
                help="Upload CSV data files",
                label_visibility="collapsed",
                accept_multiple_files=True
            )
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    try:
                        uploaded_data = pd.read_csv(uploaded_file)
                        st.success(f"✅ {uploaded_file.name} uploaded!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Export CSV button
        with col_btn2:
            st.button("Export CSV", use_container_width=True)

        # History Toggle button
        with col_btn3:
            if st.button("History", use_container_width=True):
                st.session_state.show_history = not st.session_state.show_history

        # Run Optimization button - separate container below
        st.markdown("""
        <style>
        .run-opt-container button {
            background-color: #FF0000 !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 17px !important;
            padding: 12px 24px !important;
            min-height: 50px !important;
        }
        .run-opt-container button:hover {
            background-color: #C82333 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="run-opt-container">', unsafe_allow_html=True)
        optimize_clicked = st.button("Run Optimization", use_container_width=True, key="run_opt_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        return optimize_clicked

    return False

def handle_optimization():
    """Handle optimization button click"""
    st.success("Optimization started!")
