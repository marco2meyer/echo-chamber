import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import networkx as nx
import copy
import time

from simulation import Simulation
from visualization import visualize_network, plot_metrics

# --- Global variable for simulation state (Simplification for demo) ---
# WARNING: Not suitable for multi-user production environments!
simulation_instance = None
metrics_history = []
network_pos = None

# --- Helper Functions ---
def get_default_params():
    # Consolidate default parameters
    return {
        'model_type': 'bubble',
        'num_agents': 50,
        'connection_probability_intra': 0.3,
        'connection_probability_inter': 0.05,
        'initial_belief_distribution': 'bimodal',
        'belief_update_step_size': 0.05,
        'interaction_chance': 0.5,
        'step_delay': 0.1,
        'trust_threshold': 0.5,
        'default_outsider_trust': 0.1,
        'initial_high_trust': 0.9,
        'initial_trust_setup': 'belief_based'
    }

def format_metrics_text(metrics):
    if not metrics:
        return "No metrics available."
    group_A_avg_display = f"{metrics['group_A_avg']:.3f}" if metrics['group_A_avg'] is not None else "N/A"
    group_B_avg_display = f"{metrics['group_B_avg']:.3f}" if metrics['group_B_avg'] is not None else "N/A"
    return f"""Overall Avg Belief: {metrics['avg_belief']:.3f}
Overall Std Dev:    {metrics['std_dev_belief']:.3f}
---
Group A (Initial <0.5): {metrics['group_A_count']} agents
  Avg: {group_A_avg_display}, Std: {metrics['group_A_std']:.3f}
Group B (Initial >=0.5): {metrics['group_B_count']} agents
  Avg: {group_B_avg_display}, Std: {metrics['group_B_std']:.3f}"""

# --- Dash App Initialization ---
# Use Bootstrap for better layout components
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Echo Chamber ABM "
server = app.server # Expose server for deployment

# --- App Layout ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Epistemic Bubbles vs. Echo Chambers Model"), width=12)),
    dbc.Row(dbc.Col(html.P("An agent-based model exploring C. Thi Nguyen's distinction."), width=12)),
    
    dbc.Row([
        # --- Sidebar: Parameters ---
        dbc.Col([
            html.H3("Simulation Parameters"),
            dbc.Label("Model Type:"),
            dbc.RadioItems(
                options=[
                    {"label": "Epistemic Bubble", "value": "bubble"},
                    {"label": "Echo Chamber", "value": "chamber"},
                ],
                value='bubble', # Default
                id="model-type-radio",
            ),
            html.Hr(),
            dbc.Label("Number of Agents:", html_for="num-agents-slider"),
            dcc.Slider(id="num-agents-slider", min=10, max=200, step=10, value=50, marks={i: str(i) for i in range(10, 201, 30)}),
            html.Br(),
            dbc.Label("Intra-Group Connection Prob (p_intra):", html_for="p-intra-slider"),
            dcc.Slider(id="p-intra-slider", min=0, max=1, step=0.01, value=0.3, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
            html.Br(),
            dbc.Label("Inter-Group Connection Prob (p_inter):", html_for="p-inter-slider"),
            dcc.Slider(id="p-inter-slider", min=0, max=1, step=0.01, value=0.05, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
            html.Hr(),
            dbc.Label("Initial Belief Distribution:"),
            dcc.Dropdown(
                id='initial-belief-select',
                options=[
                    {'label': 'Random', 'value': 'random'},
                    {'label': 'Bimodal', 'value': 'bimodal'},
                ],
                value='bimodal',
                clearable=False
            ),
            html.Br(),
            dbc.Label("Belief Update Step Size:", html_for="belief-step-slider"),
            dcc.Slider(id="belief-step-slider", min=0.01, max=0.5, step=0.01, value=0.05, marks={i/10: f'{i/10:.2f}' for i in range(0, 6)}),
            html.Br(),
            dbc.Label("Interaction Chance per Step:", html_for="interaction-chance-slider"),
            dcc.Slider(id="interaction-chance-slider", min=0, max=1, step=0.05, value=0.5, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
            html.Hr(),
            dbc.Label("Step Delay (seconds):", html_for="step-delay-slider"),
            dcc.Slider(id="step-delay-slider", min=0, max=2, step=0.05, value=0.1, marks={i/2: f'{i/2:.1f}' for i in range(0, 5)}),
            html.Hr(),
            # --- Echo Chamber Specific (Hidden/Shown by Callback) ---
            html.Div([
                 html.H4("Echo Chamber Settings"),
                 dbc.Label("Trust Threshold:", html_for="trust-thresh-slider"),
                 dcc.Slider(id="trust-thresh-slider", min=0, max=1, step=0.05, value=0.5, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
                 html.Br(),
                 dbc.Label("Default Outsider Trust:", html_for="default-trust-slider"),
                 dcc.Slider(id="default-trust-slider", min=0, max=1, step=0.05, value=0.1, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
                 html.Br(),
                 dbc.Label("Initial High Trust Value:", html_for="high-trust-slider"),
                 dcc.Slider(id="high-trust-slider", min=0, max=1, step=0.05, value=0.9, marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)}),
                 html.Br(),
                 dbc.Label("Initial Trust Setup:"),
                 dcc.Dropdown(
                     id='initial-trust-select',
                     options=[
                         {'label': 'Belief Based', 'value': 'belief_based'},
                         {'label': 'Uniform High', 'value': 'uniform_high'},
                     ],
                     value='belief_based',
                     clearable=False
                 ),
            ], id="echo-chamber-params", style={'display': 'none'}), # Hidden by default

        ], width=4),
        
        # --- Main Area: Controls & Visualization ---
        dbc.Col([
            # --- Controls ---
            dbc.Row([
                dbc.Col(dbc.Button("Setup / Reset", id="setup-button", color="primary", className="me-1"), width="auto"),
                dbc.Col(dbc.Button("Start / Resume", id="start-button", color="success", className="me-1"), width="auto"),
                dbc.Col(dbc.Button("Pause", id="pause-button", color="warning", className="me-1"), width="auto"),
            ], className="mb-3"),
            
            # --- Visualization & Metrics Columns ---
            dbc.Row([
                dbc.Col([
                    html.H4("Network Visualization"),
                    dcc.Graph(id='network-graph', figure=go.Figure()) # Placeholder figure
                ], width=7),
                dbc.Col([
                    html.H4("Simulation Metrics"),
                    html.Pre(id='metrics-display', children="Setup simulation to view metrics."),
                    dcc.Graph(id='metrics-plot', figure=go.Figure()) # Placeholder figure
                ], width=5),
            ]),
        ], width=8),
    ]),
    
    # --- Hidden Components ---
    # Interval timer for simulation steps
    dcc.Interval(id='simulation-interval', interval=1000, n_intervals=0, disabled=True),
    # Store for run state (running or paused)
    dcc.Store(id='run-state-store', data={'running': False}),
    # Store for current parameters (to avoid passing all individually)
    dcc.Store(id='params-store', data=get_default_params()),
], fluid=True)

# --- Callbacks ---

# Callback to show/hide Echo Chamber parameters
@app.callback(
    Output('echo-chamber-params', 'style'),
    Input('model-type-radio', 'value')
)
def toggle_echo_chamber_params(model_type):
    if model_type == 'chamber':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Callback to store parameters when they change
@app.callback(
    Output('params-store', 'data'),
    # --- Inputs for ALL parameters ---
    Input('model-type-radio', 'value'),
    Input('num-agents-slider', 'value'),
    Input('p-intra-slider', 'value'),
    Input('p-inter-slider', 'value'),
    Input('initial-belief-select', 'value'),
    Input('belief-step-slider', 'value'),
    Input('interaction-chance-slider', 'value'),
    Input('step-delay-slider', 'value'),
    Input('trust-thresh-slider', 'value'),
    Input('default-trust-slider', 'value'),
    Input('high-trust-slider', 'value'),
    Input('initial-trust-select', 'value')
)
def update_params_store(model_type, num_agents, p_intra, p_inter, 
                        initial_belief, step_size, interaction_chance, delay, 
                        trust_thresh, default_trust, high_trust, trust_setup):
    return {
        'model_type': model_type,
        'num_agents': num_agents,
        'connection_probability_intra': p_intra,
        'connection_probability_inter': p_inter,
        'initial_belief_distribution': initial_belief,
        'belief_update_step_size': step_size,
        'interaction_chance': interaction_chance,
        'step_delay': delay,
        'trust_threshold': trust_thresh,
        'default_outsider_trust': default_trust,
        'initial_high_trust': high_trust,
        'initial_trust_setup': trust_setup
    }

# Callback to handle Setup, Start, Pause buttons
@app.callback(
    Output('run-state-store', 'data'),
    Output('simulation-interval', 'disabled'),
    Output('simulation-interval', 'interval'), # Allow changing speed
    # Need Outputs for initial display on Setup (handled by interval callback)
    Input('setup-button', 'n_clicks'),
    Input('start-button', 'n_clicks'),
    Input('pause-button', 'n_clicks'),
    State('params-store', 'data'),
    State('run-state-store', 'data'),
    prevent_initial_call=True
)
def handle_controls(setup_clicks, start_clicks, pause_clicks, params, run_state):
    global simulation_instance, metrics_history, network_pos
    
    triggered_id = callback_context.triggered_id
    running = run_state['running']
    disabled = True
    interval = max(10, int(params.get('step_delay', 0.1) * 1000)) # Interval in ms

    if triggered_id == 'setup-button':
        print("Setup button clicked")
        simulation_instance = Simulation(copy.deepcopy(params))
        metrics_history = []
        network_pos = None # Reset position
        running = False
        disabled = True
        # Add initial metric point
        sim_state = simulation_instance.get_simulation_state()
        if sim_state['network']:
             network_pos = nx.spring_layout(sim_state['network'], seed=42)
        initial_metrics = simulation_instance.calculate_metrics()
        initial_metrics['time_step'] = 0
        metrics_history.append(initial_metrics)
        print("Simulation Setup Complete")
        
    elif triggered_id == 'start-button' and simulation_instance:
        print("Start button clicked")
        running = True
        disabled = False
        
    elif triggered_id == 'pause-button':
        print("Pause button clicked")
        running = False
        disabled = True
        
    return {'running': running}, disabled, interval

# Callback for simulation step and visualization update
@app.callback(
    Output('network-graph', 'figure'),
    Output('metrics-plot', 'figure'),
    Output('metrics-display', 'children'),
    Input('simulation-interval', 'n_intervals'),
    Input('setup-button', 'n_clicks'), # Trigger update on setup too
    State('run-state-store', 'data')
)
def run_simulation_step(n_intervals, setup_clicks, run_state):
    global simulation_instance, metrics_history, network_pos
    
    # Determine if update is due to setup or interval
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id
    is_setup_trigger = triggered_id == 'setup-button'

    if simulation_instance is None:
        # No simulation initialized yet
        return go.Figure(), go.Figure(), "Setup simulation to start."
    
    sim_state = simulation_instance.get_simulation_state()
    running = run_state['running']
    
    # Perform step if running AND triggered by interval (not setup)
    if running and not is_setup_trigger:
        try:
            simulation_instance.simulation_step()
            sim_state = simulation_instance.get_simulation_state() # Get updated state
            current_metrics = simulation_instance.calculate_metrics()
            current_metrics['time_step'] = sim_state['time_step']
            if not metrics_history or metrics_history[-1]['time_step'] != current_metrics['time_step']:
                metrics_history.append(current_metrics)
        except Exception as e:
            print(f"Error during simulation step: {e}")
            # Stop simulation on error (optional)
            # We might need to update run_state_store here, but that requires another callback structure
            pass 
            
    # Always generate visuals based on the current state
    
    # Network plot
    if network_pos is None and sim_state['network']:
         network_pos = nx.spring_layout(sim_state['network'], seed=42)
         
    network_fig = visualize_network(sim_state, network_pos)
    if network_fig is None:
        network_fig = go.Figure()

    # Metrics plot
    metrics_fig = plot_metrics(metrics_history)
    if metrics_fig is None:
        metrics_fig = go.Figure()
        
    # Metrics text
    metrics_text = "No metrics yet." 
    if metrics_history:
        metrics_text = format_metrics_text(metrics_history[-1])
        
    return network_fig, metrics_fig, html.Pre(metrics_text) # Use html.Pre for formatted text

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True) 