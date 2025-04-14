import streamlit as st
import networkx as nx
# Remove matplotlib import if no longer needed elsewhere
# import matplotlib.pyplot as plt 
import plotly.graph_objects as go # Import Plotly
import time
import copy # To deep copy simulation state for modifications
import pandas as pd # For metrics DataFrame
import plotly.express as px # Import plotly express for default colors

from simulation import Simulation

# --- Visualization Function (Updated for FIXED Group Symbols) ---
def visualize_network(sim_state, drawing_placeholder):
    """Draws the network state using Plotly, differentiating fixed groups by symbol."""
    agents = sim_state['agents']
    network = sim_state['network']
    time_step = sim_state['time_step']
    model_type = sim_state['model_type']

    if not network or not agents:
        drawing_placeholder.text("Simulation not initialized or no agents.")
        return

    # Get positions for nodes (layout algorithm)
    # Use a cached layout if available, otherwise compute
    if 'layout' not in st.session_state or st.session_state.layout_params_changed:
        st.session_state.pos = nx.spring_layout(network, seed=42) # Use a seed for consistent layout
        st.session_state.layout_params_changed = False # Reset flag
    pos = st.session_state.pos

    # --- Create Plotly Figure ---

    # 1. Edge Trace
    edge_x = []
    edge_y = []
    for edge in network.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None]) # None creates gaps between lines
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # 2. Node Trace (Updated for FIXED Symbols)
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_symbols = []
    node_ids = list(network.nodes())

    for node_id in node_ids:
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        agent = agents[node_id]
        belief_str = f"Belief: {agent.belief_state:.3f}"
        trust_info = ""
        # Add trust info for echo chamber model on hover
        if model_type == 'chamber' and agent.trust_scores:
            avg_trust = sum(agent.trust_scores.values()) / len(agent.trust_scores) if agent.trust_scores else 0
            trust_info = f"<br>Avg Trust Given: {avg_trust:.2f}"
            
        # Use the FIXED agent.group attribute for symbol
        group = agent.group
        symbol = "circle" if group == 'A' else "square"
        
        node_text.append(f"Agent ID: {agent.id}<br>Group: {group}<br>{belief_str}{trust_info}")
        node_colors.append(agent.belief_state) # Use belief for color scale
        node_symbols.append(symbol)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options: 'Greys', 'YlGnBu', 'Greens', 'YlOrRd', 'Bluered', 'RdBu',
            # 'Reds', 'Blues', 'Picnic', 'Rainbow', 'Portland', 'Jet', 'Hot', 'Blackbody',
            # 'Earth', 'Electric', 'Viridis', 'Cividis'
            colorscale='RdBu', # Correct Plotly name for Red-Blue scale
            reversescale=False,
            color=node_colors,
            size=10,
            symbol=node_symbols, # Use the list of fixed symbols
            colorbar=dict(
                thickness=15,
                title=dict(text='Belief State', side='right'),
                xanchor='left'
            ),
            line_width=1,
            line_color='#333'
            ),
        text=node_text # Text that appears on hover
        )

    # 3. Create Figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=dict(
                        text=f'Network State at Time Step: {time_step} ({model_type.capitalize()})',
                        font=dict(size=16)
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Visualization by Plotly",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    # Display in Streamlit
    drawing_placeholder.plotly_chart(fig, use_container_width=True, key="network_plot")

# --- Metrics Plotting Function (Updated for Styling) ---
def plot_metrics(metrics_history):
    """Plots the history of simulation metrics using Plotly with specific styling."""
    if not metrics_history or len(metrics_history) < 1:
        return None

    df = pd.DataFrame(metrics_history)
    df = df.dropna(axis=1, how='all')

    fig = go.Figure()

    # Get default Plotly colors
    colors = px.colors.qualitative.Plotly
    color_A = colors[0] # Default blue
    color_B = colors[1] # Default orange

    # Plot Group A Avg (Thick)
    if 'group_A_avg' in df.columns:
        fig.add_trace(go.Scatter(x=df['time_step'], y=df['group_A_avg'], mode='lines+markers', 
                                 name='Avg Belief (Grp A)', line=dict(color=color_A, width=3)))
    
    # Plot Group B Avg (Thick)
    if 'group_B_avg' in df.columns:
        fig.add_trace(go.Scatter(x=df['time_step'], y=df['group_B_avg'], mode='lines+markers', 
                                 name='Avg Belief (Grp B)', line=dict(color=color_B, width=3)))
    
    # --- Remove Std Dev Plotting ---
    # # Plot Group A Std Dev (Thin, matching color)
    # if 'group_A_std' in df.columns:
    #     fig.add_trace(go.Scatter(x=df['time_step'], y=df['group_A_std'], mode='lines+markers', 
    #                              name='Std Dev (Grp A)', yaxis="y2", line=dict(color=color_A, width=1)))
    # 
    # # Plot Group B Std Dev (Thin, matching color)
    # if 'group_B_std' in df.columns:
    #     fig.add_trace(go.Scatter(x=df['time_step'], y=df['group_B_std'], mode='lines+markers', 
    #                              name='Std Dev (Grp B)', yaxis="y2", line=dict(color=color_B, width=1)))
    # --- End Removal ---

    # Update layout (Remove secondary y-axis)
    fig.update_layout(
        title="Group Average Belief Over Time",
        xaxis_title="Time Step",
        yaxis=dict(
            title="Average Belief",
            range=[0, 1]
        ),
        # --- Remove yaxis2 ---
        # yaxis2=dict(
        #     title="Standard Deviation",
        #     overlaying="y",
        #     side="right",
        # ),
        # --- End Removal ---
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    return fig

# --- Streamlit App Layout ---
st.set_page_config(layout="wide") # Use wider layout
st.title("Epistemic Bubbles vs. Echo Chambers ABM")
st.markdown("An agent-based model exploring C. Thi Nguyen's distinction.")

# --- Simulation Parameters (Sidebar - Updated Network Params) ---
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
model_type = st.sidebar.radio(
    "Select Model Type:",
    ('bubble', 'chamber'),
    format_func=lambda x: {'bubble': 'Epistemic Bubble', 'chamber': 'Echo Chamber'}[x],
    key='model_type_radio'
)

# --- Core Parameters (Updated Network Params) ---
num_agents = st.sidebar.slider("Number of Agents", 10, 200, 50, key='num_agents_slider')
st.sidebar.markdown("--- Network Connectivity ---")
connection_probability_intra = st.sidebar.slider("Intra-Group Connection Prob (p_intra)", 0.0, 1.0, 0.3, 0.01, key='p_intra_slider')
connection_probability_inter = st.sidebar.slider("Inter-Group Connection Prob (p_inter)", 0.0, 1.0, 0.05, 0.01, key='p_inter_slider')

initial_belief_distribution = st.sidebar.selectbox(
    "Initial Belief Distribution",
    ('random', 'bimodal'), # 'uniform' needs clearer definition
    index=1, # Default to bimodal
    key='initial_belief_select'
)
belief_update_step_size = st.sidebar.slider("Belief Update Step Size", 0.01, 0.5, 0.05, 0.01, key='belief_step_slider')
interaction_chance = st.sidebar.slider("Interaction Chance per Step", 0.0, 1.0, 0.5, 0.05, key='interaction_chance_slider')

# --- Simulation Speed Control ---
step_delay = st.sidebar.slider(
    "Step Delay (seconds)",
    0.0, 2.0, 0.1, 0.05, # Min, Max, Default, Step
    help="Pause between simulation steps for visualization.",
    key='step_delay_slider'
)

# --- Echo Chamber Specific Parameters (Conditional) ---
default_outsider_trust = 0.1 # Define defaults here
trust_threshold = 0.5
initial_trust_setup = 'belief_based'

if model_type == 'chamber':
    st.sidebar.markdown("--- Echo Chamber Settings ---")
    trust_threshold = st.sidebar.slider("Trust Threshold (for belief update)", 0.0, 1.0, 0.5, 0.05, key='trust_thresh_slider')
    default_outsider_trust = st.sidebar.slider("Default Trust for Unknown/Distrusted Agents", 0.0, 1.0, 0.1, 0.05, key='default_trust_slider')
    initial_trust_setup = st.sidebar.selectbox(
        "Initial Trust Setup",
        ('belief_based', 'uniform_high'),
        index=0, # Default to belief_based
        help="'belief_based': Trust agents with similar initial beliefs more. 'uniform_high': Initially trust everyone highly.",
        key='initial_trust_select'
    )

# Store parameters in a dictionary (Updated)
params = {
    'model_type': model_type,
    'num_agents': num_agents,
    'connection_probability_intra': connection_probability_intra,
    'connection_probability_inter': connection_probability_inter,
    'initial_belief_distribution': initial_belief_distribution,
    'belief_update_step_size': belief_update_step_size,
    'interaction_chance': interaction_chance,
    'step_delay': step_delay,
    'trust_threshold': trust_threshold,
    'default_outsider_trust': default_outsider_trust,
    'initial_trust_setup': initial_trust_setup
}

# --- Main Layout with Columns for Network and Metrics ---
col_network, col_metrics = st.columns([3, 2]) # Adjust ratio as needed (e.g., 2, 1)

with col_network:
    st.subheader("Network Visualization")
    # Define placeholder for the network plot
    vis_placeholder = st.empty()

with col_metrics:
    st.subheader("Simulation Metrics")
    # Placeholders for current metrics
    metrics_display_placeholder = st.empty()
    # Placeholder for the metrics plot
    metrics_plot_placeholder = st.empty()

# --- Control Buttons (Placed below columns for better flow) ---
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
        else:
             st.session_state.layout_params_changed = True # First setup

        st.session_state.simulation_instance = Simulation(copy.deepcopy(params))
        st.session_state.running = False
        st.session_state.metrics_history = [] # Reset metrics history
        st.success("Simulation Initialized/Reset!")

        # Calculate and display initial metrics
        sim_state = st.session_state.simulation_instance.get_simulation_state()
        current_metrics = st.session_state.simulation_instance.calculate_metrics()
        current_metrics['time_step'] = sim_state['time_step']
        st.session_state.metrics_history.append(current_metrics)
        
        # Display current metrics text (Updated)
        group_A_avg_val = current_metrics['group_A_avg']
        group_A_avg_display = f"{group_A_avg_val:.3f}" if group_A_avg_val is not None else "N/A"
        group_B_avg_val = current_metrics['group_B_avg']
        group_B_avg_display = f"{group_B_avg_val:.3f}" if group_B_avg_val is not None else "N/A"
        
        # Use fixed group names in text
        metrics_text = f"""Overall Avg Belief: {current_metrics['avg_belief']:.3f}
Overall Std Dev:    {current_metrics['std_dev_belief']:.3f}
---
Group A (Initial <0.5): {current_metrics['group_A_count']} agents
  Avg: {group_A_avg_display}, Std: {current_metrics['group_A_std']:.3f}
Group B (Initial >=0.5): {current_metrics['group_B_count']} agents
  Avg: {group_B_avg_display}, Std: {current_metrics['group_B_std']:.3f}"""
        metrics_display_placeholder.markdown(f"```\n{metrics_text}\n```")

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

# --- Simulation Loop (REVISED STRUCTURE 3 - Updated metrics display) ---
if st.session_state.simulation_instance:
    sim = st.session_state.simulation_instance
    needs_rerun = False
    sim_state = None

    if st.session_state.running:
        try:
            sim.simulation_step()
            sim_state = sim.get_simulation_state()
            current_metrics = sim.calculate_metrics()
            current_metrics['time_step'] = sim_state['time_step']
            if not st.session_state.metrics_history or st.session_state.metrics_history[-1]['time_step'] != current_metrics['time_step']:
                st.session_state.metrics_history.append(current_metrics)
            needs_rerun = True
        except Exception as e:
            st.error(f"An error occurred during simulation step: {e}")
            st.session_state.running = False
            sim_state = sim.get_simulation_state()
    else:
        sim_state = sim.get_simulation_state()

    if sim_state:
        visualize_network(sim_state, vis_placeholder)
        if st.session_state.metrics_history:
            last_metrics = st.session_state.metrics_history[-1]
            # Update metrics text display
            group_A_avg_val = last_metrics['group_A_avg']
            group_A_avg_display = f"{group_A_avg_val:.3f}" if group_A_avg_val is not None else "N/A"
            group_B_avg_val = last_metrics['group_B_avg']
            group_B_avg_display = f"{group_B_avg_val:.3f}" if group_B_avg_val is not None else "N/A"
            # Use fixed group names in text
            metrics_text = f"""Overall Avg Belief: {last_metrics['avg_belief']:.3f}
Overall Std Dev:    {last_metrics['std_dev_belief']:.3f}
---
Group A (Initial <0.5): {last_metrics['group_A_count']} agents
  Avg: {group_A_avg_display}, Std: {last_metrics['group_A_std']:.3f}
Group B (Initial >=0.5): {last_metrics['group_B_count']} agents
  Avg: {group_B_avg_display}, Std: {last_metrics['group_B_std']:.3f}"""
            metrics_display_placeholder.markdown(f"```\n{metrics_text}\n```")
            metrics_fig = plot_metrics(st.session_state.metrics_history)
            if metrics_fig:
                metrics_plot_placeholder.plotly_chart(metrics_fig, use_container_width=True, key="metrics_plot")
            else:
                metrics_plot_placeholder.empty()
        else:
            metrics_display_placeholder.empty()
            metrics_plot_placeholder.empty()

    if needs_rerun:
        sleep_duration = sim.params.get('step_delay', 0.1)
        time.sleep(sleep_duration)
        st.rerun()
else:
    vis_placeholder.info("Setup the simulation using the parameters in the sidebar and click 'Setup / Reset Simulation'.")
    metrics_display_placeholder.empty()
    metrics_plot_placeholder.empty()

# --- Optional: Display Raw Parameters ---
# with st.expander("Show Current Parameters"):
#     st.json(params) 