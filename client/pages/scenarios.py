import streamlit as st

def display_scenarios_tab():
    """Display Scenario Analysis tab content"""
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
