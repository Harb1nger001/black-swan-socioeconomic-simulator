import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
from run_simulation import run_simulation

st.set_page_config(layout="wide")
st.title("🧠 Black Swan Socioeconomic Simulation Dashboard")

agents_tab, economics_tab, shocks_tab, advanced_tab = st.tabs(["🧍 Agents", "📈 Economics", "🧨 Shocks", "⚙️ Advanced"])

with agents_tab:
    n_households = st.slider("Number of Households", 10, 2000, 100)
    n_firms = st.slider("Number of Firms", 5, 500, 20)

with economics_tab:
    simulation_years = st.slider("Simulation Years", 1, 20, 10)
    simulation_steps = simulation_years * 365
    initial_inflation = st.slider("Initial Inflation Rate", 0.0, 1.0, 0.03)
    initial_unrest = st.slider("Initial Unrest Level", 0, 100, 0)
    initial_employment = st.slider("Initial Employment Rate", 0.0, 1.0, 0.95)

with shocks_tab:
    st.markdown("Enter time step for each shock (0 = disabled):")
    shock_schedule = {
        "💥 Financial Crisis": st.number_input("Financial Crisis Step", min_value=0, max_value=simulation_steps, value=0),
        "🔥 Political Instability": st.number_input("Political Instability Step", min_value=0, max_value=simulation_steps, value=0),
        "🦠 Pandemic": st.number_input("Pandemic Step", min_value=0, max_value=simulation_steps, value=0),
        "⚡ Tech Collapse": st.number_input("Tech Collapse Step", min_value=0, max_value=simulation_steps, value=0),
        "🌪️ Natural Disaster": st.number_input("Natural Disaster Step", min_value=0, max_value=simulation_steps, value=0)
    }
    active_shocks = {k: v for k, v in shock_schedule.items() if v > 0}

with advanced_tab:
    step_mode = st.checkbox("Enable Manual Step Mode")
    enable_networks = st.checkbox("Show Agent Networks", value=True)
    enable_live_plot = st.checkbox("Live Economic Charting", value=True)

if st.button("🚀 Run Simulation"):
    st.info("Running simulation... this may take a few seconds.")
    placeholder_chart = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    shock_display = st.empty()

    live_df = pd.DataFrame(columns=["step", "Inflation", "Unrest", "GDPGrowthRate"])

    params = {
        'steps': simulation_steps,
        'num_households': n_households,
        'num_firms': n_firms,
        'init_inflation_rate': initial_inflation,
        'init_unrest': initial_unrest,
        'init_employment_rate': initial_employment,
        'shock_steps': list(active_shocks.values()),
        'shock_labels': list(active_shocks.keys())
    }

    def update_progress(i, var_data):
        progress_bar.progress(int(i / simulation_steps * 100))
        status_text.text(f"Step {i} of {simulation_steps}")
        if i in params['shock_steps']:
            shock_index = params['shock_steps'].index(i)
            shock_display.warning(f"⚠️ Shock at step {i} - {params['shock_labels'][shock_index]}")

        row = {"step": i}
        for k in live_df.columns[1:]:
            row[k] = var_data.get(k, None)
        live_df.loc[len(live_df)] = row

        if enable_live_plot and i % 10 == 0:
            chart = px.line(live_df, x="step", y=live_df.columns[1:], title="📊 Live Economic Metrics")
            placeholder_chart.plotly_chart(chart, use_container_width=True)

    model, results = run_simulation(params, live=True, update_callback=update_progress)

    st.success("Simulation Complete ✅")

    df = results
    df.index = df.index + 1

    st.subheader("📊 Final Results Snapshot")
    st.dataframe(df.tail(20))

    st.subheader("📈 Final Economic Indicators")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(df, y="GDPGrowthRate", title="GDP Growth Rate"), use_container_width=True)
        st.plotly_chart(px.line(df, y="Inflation", title="Inflation Rate"), use_container_width=True)
        st.plotly_chart(px.line(df, y="EmploymentRate", title="Employment Rate"), use_container_width=True)
    with col2:
        st.plotly_chart(px.line(df, y="Unrest", title="Social Unrest"), use_container_width=True)
        st.plotly_chart(px.line(df, y="AvgFirmProfit", title="Average Firm Profit"), use_container_width=True)
        st.plotly_chart(px.line(df, y="GiniCoefficient", title="Gini Coefficient"), use_container_width=True)

    if active_shocks:
        st.subheader("⏱️ Shock Timeline")
        st.table(pd.DataFrame({
            "Shock": params['shock_labels'],
            "Step": params['shock_steps']
        }).sort_values("Step"))

    if enable_networks:
        st.subheader("🔗 Agent Networks")

        def plot_network(G, title):
            pos = nx.spring_layout(G, seed=42)
            fig, ax = plt.subplots(figsize=(6, 4))
            nx.draw_networkx(G, pos, ax=ax, node_size=60, font_size=8, with_labels=False)
            st.pyplot(fig)

        st.markdown("**🏠 Household Influence Network**")
        plot_network(model.household_graph, "Household Network")

        st.markdown("**🏢 Policy Network (Firms/Government)**")
        plot_network(model.policy_graph, "Firm-Govt Policy Graph")
