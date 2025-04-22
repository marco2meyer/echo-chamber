import streamlit as st
import networkx as nx
# No longer need plotly imports here if figs come from visualization.py
# import plotly.graph_objects as go 
# import plotly.express as px 
import time
import copy
import pandas as pd

from simulation import Simulation
# Import visualization functions
from visualization import visualize_network, plot_metrics 

# --- Visualization Function Definitions Removed ---
# (visualize_network and plot_metrics moved to visualization.py)

# --- Streamlit App Layout ---
# ... (page setup remains the same) ...
st.set_page_config(layout="wide")
st.title("[Streamlit] Epistemic Bubbles vs. Echo Chambers ABM") # Add [Streamlit] to title
st.markdown("An agent-based model exploring C. Thi Nguyen's distinction.")

# --- Simulation Parameters (Sidebar - Updated Network Params) ---
# ... (sidebar setup remains the same) ...
st.sidebar.header("Simulation Parameters")

# Use session state to keep track of parameters and simulation object
if 'simulation_instance' not in st.session_state:
    st.session_state.simulation_instance = None
if 'running' not in st.session_state:
    st.session_state.running = False
if 'layout' not in st.session_state:
    st.session_state.pos = None
if 'layout_params_changed' not in st.session_state:
    st.session_state.layout_params_changed = True # Initially true to compute layout
# Add session state for metrics history
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# --- Model Selection ---
# ... (remains the same) ...
model_type = st.sidebar.radio(
    "Select Model Type:",
    ('bubble', 'chamber'),
    format_func=lambda x: {'bubble': 'Epistemic Bubble', 'chamber': 'Echo Chamber'}[x],
    key='model_type_radio'
)

# --- Core Parameters (Updated Network Params) ---
# ... (remains the same) ...
num_agents = st.sidebar.slider("Number of Agents", 10, 200, 50, key='num_agents_slider')
st.sidebar.markdown("--- Network Connectivity ---")
connection_probability_intra = st.sidebar.slider("Intra-Group Connection Prob (p_intra)", 0.0, 1.0, 0.3, 0.01, key='p_intra_slider')
connection_probability_inter = st.sidebar.slider("Inter-Group Connection Prob (p_inter)", 0.0, 1.0, 0.05, 0.01, key='p_inter_slider')

initial_belief_distribution = st.sidebar.selectbox(
    "Initial Belief Distribution",
    ('random', 'bimodal'),
    index=1, # Default to bimodal
    key='initial_belief_select'
)
belief_update_step_size = st.sidebar.slider("Belief Update Step Size", 0.01, 0.5, 0.05, 0.01, key='belief_step_slider')
interaction_chance = st.sidebar.slider("Interaction Chance per Step", 0.0, 1.0, 0.5, 0.05, key='interaction_chance_slider')

# --- Simulation Speed Control ---
# ... (remains the same) ...
step_delay = st.sidebar.slider(
    "Step Delay (seconds)",
    0.0, 2.0, 0.1, 0.05, # Min, Max, Default, Step
    help="Pause between simulation steps for visualization.",
    key='step_delay_slider'
)

# --- Echo Chamber Specific Parameters (Conditional) ---
# ... (remains the same) ...
default_outsider_trust = 0.1 # Define defaults here
trust_threshold = 0.5
initial_trust_setup = 'belief_based'
initial_high_trust = 0.9 # Define default value BEFORE the if block

if model_type == 'chamber':
    st.sidebar.markdown("--- Echo Chamber Settings ---")
    trust_threshold = st.sidebar.slider("Trust Threshold (for belief update)", 0.0, 1.0, 0.5, 0.05, key='trust_thresh_slider')
    default_outsider_trust = st.sidebar.slider("Default Trust for Unknown/Distrusted Agents", 0.0, 1.0, 0.1, 0.05, key='default_trust_slider')
    # The slider will overwrite the default value if model is chamber
    initial_high_trust = st.sidebar.slider("Initial High Trust Value (for Setup)", 0.0, 1.0, initial_high_trust, 0.05, key='high_trust_slider')
    initial_trust_setup = st.sidebar.selectbox(
        "Initial Trust Setup",
        ('belief_based', 'uniform_high'),
        index=0, # Default to belief_based
        help="'belief_based': Trust agents with similar initial beliefs more. 'uniform_high': Initially trust everyone highly.",
        key='initial_trust_select'
    )

# Store parameters in a dictionary (Updated)
# ... (remains the same) ...
params = {
    'model_type': model_type,
    'num_agents': num_agents,
    'connection_probability_intra': connection_probability_intra, # Added
    'connection_probability_inter': connection_probability_inter, # Added
    'initial_belief_distribution': initial_belief_distribution,
    'belief_update_step_size': belief_update_step_size,
    'interaction_chance': interaction_chance,
    'step_delay': step_delay,
    'trust_threshold': trust_threshold,
    'default_outsider_trust': default_outsider_trust,
    'initial_high_trust': initial_high_trust,
    'initial_trust_setup': initial_trust_setup
}

# --- Define Control Buttons FIRST ---
# ... (button definitions remain the same) ...
st.markdown("--- Controls ---")
control_cols = st.columns(3)

with control_cols[0]:
    if st.button("Setup / Reset Simulation", key='setup_button'):
        # Indicate that layout needs recalculation if N or connection prob changes
        if st.session_state.simulation_instance:
            old_params = st.session_state.simulation_instance.params
            # Check against new parameters for layout change
            if old_params['num_agents'] != num_agents or \
               old_params.get('connection_probability_intra', -1) != connection_probability_intra or \
               old_params.get('connection_probability_inter', -1) != connection_probability_inter:
                st.session_state.layout_params_changed = True
            # Also recalculate layout if structure params change
            st.session_state.pos = None # Force layout recalculation
        else:
             st.session_state.layout_params_changed = True # First setup
             st.session_state.pos = None # Ensure layout calculated on first setup

        st.session_state.simulation_instance = Simulation(copy.deepcopy(params))
        st.session_state.running = False
        st.session_state.metrics_history = [] # Reset metrics history
        st.success("Simulation Initialized/Reset!")

        # Calculate initial metrics (but don't display text here yet)
        sim_state = st.session_state.simulation_instance.get_simulation_state()
        # Calculate positions for the first draw
        if st.session_state.pos is None and sim_state['network']:
             st.session_state.pos = nx.spring_layout(sim_state['network'], seed=42)
             st.session_state.layout_params_changed = False

        current_metrics = st.session_state.simulation_instance.calculate_metrics()
        current_metrics['time_step'] = sim_state['time_step']
        st.session_state.metrics_history.append(current_metrics)
        # Display text will happen in the main loop display section

with control_cols[1]:
    if st.button("Start / Resume", key='start_button'):
        if st.session_state.simulation_instance:
            st.session_state.running = True
            st.info("Simulation Running...")
        else:
            st.warning("Please Setup the simulation first.")

with control_cols[2]:
    if st.button("Pause", key='pause_button'):
        st.session_state.running = False
        st.info("Simulation Paused.")

st.markdown("--- Visualization & Metrics ---")

# --- Main Layout with Columns for Network and Metrics ---
# ... (column setup remains the same) ...
col_network, col_metrics = st.columns([3, 2])

with col_network:
    vis_placeholder = st.empty()

with col_metrics:
    metrics_display_placeholder = st.empty()
    metrics_plot_placeholder = st.empty()


# --- Simulation Loop (REVISED STRUCTURE 3 - Updated metrics display) ---
if st.session_state.simulation_instance:
    sim = st.session_state.simulation_instance
    needs_rerun = False
    sim_state = None # Initialize

    # Logic to determine the state to display *before* drawing
    if st.session_state.running:
        try:
            # Run step and update state
            sim.simulation_step()
            sim_state = sim.get_simulation_state()

            # Calculate and store metrics for the *new* state
            current_metrics = sim.calculate_metrics()
            current_metrics['time_step'] = sim_state['time_step']
            if not st.session_state.metrics_history or st.session_state.metrics_history[-1]['time_step'] != current_metrics['time_step']:
                st.session_state.metrics_history.append(current_metrics)

            # Schedule a rerun for the next step
            needs_rerun = True

        except Exception as e:
            st.error(f"An error occurred during simulation step: {e}")
            st.session_state.running = False
            sim_state = sim.get_simulation_state()
    else:
        sim_state = sim.get_simulation_state()

    # --- Drawing happens once per script run, *after* state is determined ---
    if sim_state:
        # Ensure layout exists for visualization function
        if st.session_state.pos is None and sim_state['network']:
             st.session_state.pos = nx.spring_layout(sim_state['network'], seed=42)
             st.session_state.layout_params_changed = False # Should be false now

        # Visualize Network based on the determined state using imported function
        network_fig = visualize_network(sim_state, st.session_state.pos) 
        if network_fig:
            vis_placeholder.plotly_chart(network_fig, use_container_width=True, key="network_plot")
        else:
             vis_placeholder.text("Network data not available for plotting.")

        # Display Metrics based on history using imported function
        if st.session_state.metrics_history:
            last_metrics = st.session_state.metrics_history[-1]
            # Update metrics text display
            group_A_avg_val = last_metrics['group_A_avg']
            group_A_avg_display = f"{group_A_avg_val:.3f}" if group_A_avg_val is not None else "N/A"
            group_B_avg_val = last_metrics['group_B_avg']
            group_B_avg_display = f"{group_B_avg_val:.3f}" if group_B_avg_val is not None else "N/A"
            metrics_text = f"""Overall Avg Belief: {last_metrics['avg_belief']:.3f}
Overall Std Dev:    {last_metrics['std_dev_belief']:.3f}
---
Group A (Initial <0.5): {last_metrics['group_A_count']} agents
  Avg: {group_A_avg_display}, Std: {last_metrics['group_A_std']:.3f}
Group B (Initial >=0.5): {last_metrics['group_B_count']} agents
  Avg: {group_B_avg_display}, Std: {last_metrics['group_B_std']:.3f}"""
            metrics_display_placeholder.markdown(f"```\n{metrics_text}\n```")
            
            # Plot metrics using imported function
            metrics_fig = plot_metrics(st.session_state.metrics_history)
            if metrics_fig:
                metrics_plot_placeholder.plotly_chart(metrics_fig, use_container_width=True, key="metrics_plot")
            else:
                metrics_plot_placeholder.empty()
        else:
            metrics_display_placeholder.empty()
            metrics_plot_placeholder.empty()

    # Trigger rerun if a step was successfully executed
    if needs_rerun:
        sleep_duration = sim.params.get('step_delay', 0.1)
        time.sleep(sleep_duration)
        st.rerun()

else:
    # Initial message when no simulation is set up
    vis_placeholder.info("Setup the simulation using the parameters in the sidebar and click 'Setup / Reset Simulation'.")
    metrics_display_placeholder.empty()
    metrics_plot_placeholder.empty()

# --- Optional: Display Raw Parameters ---
# with st.expander("Show Current Parameters"):
#     st.json(params) 