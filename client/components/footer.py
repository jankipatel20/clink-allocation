import streamlit as st

def display_footer():
    """Display footer section"""
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
