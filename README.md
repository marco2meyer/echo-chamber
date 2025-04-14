\# Agent-Based Model: Epistemic Bubbles vs. Echo Chambers

This project implements a simple agent-based model (ABM) in Python to explore the conceptual distinction between Epistemic Bubbles and Echo Chambers, based on the work of C. Thi Nguyen.

The simulation is presented using an interactive web application built with Streamlit.

## Core Concepts

*   **Epistemic Bubble:** A situation where an individual's information sources are limited *by omission*. Certain relevant voices or perspectives are simply not included in their network, leading to an incomplete picture without necessarily involving active distrust.
*   **Echo Chamber:** A situation where an individual actively distrusts sources outside their community. It's not just about missing information; it's about *discrediting* information from outside sources based on manipulated trust.

## Model Implementation

*   **Agents:** Each agent has a belief state (represented as a float between 0 and 1) and connections to other agents.
*   **Network:** Agents are connected in a network (currently a random Erdős-Rényi graph, configurable by connection probability).
*   **Interaction:** In each time step, a random agent potentially interacts with one of its neighbors. The interaction involves the sender sharing their belief state.
*   **Belief Update:**
    *   **Epistemic Bubble Model:** The receiving agent updates its belief slightly towards the sender's belief, *regardless* of the sender (as long as they are connected). The limitation comes purely from the network structure.
    *   **Echo Chamber Model:** The receiving agent first checks its *trust* in the sender. If the sender's trust score is above a threshold, the receiver updates its belief towards the sender's. If the trust score is below the threshold, the message is ignored (actively discredited).
*   **Trust (Echo Chamber):** Agents maintain trust scores for other agents. Initial trust can be set based on belief similarity or uniformly high. (Trust dynamics/updates during the simulation are currently placeholders).

## Files

*   `app.py`: The main Streamlit application file. Run this to start the simulation.
*   `simulation.py`: Contains the `Simulation` class that manages the overall simulation state, setup, and stepping logic.
*   `agent.py`: Defines the `Agent` class with its properties and methods.
*   `models.py`: Implements the distinct belief update logic (`receive_message_bubble`, `receive_message_chamber`) for the two models.
*   `network_utils.py`: Contains functions for creating the network structure (using `networkx`).
*   `requirements.txt`: Lists the necessary Python libraries.

## Setup and Running

1.  **Clone the repository (or ensure you have the files).**
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

This will open the interactive simulation in your web browser.

## Using the Application

1.  **Sidebar Parameters:** Adjust the simulation parameters in the sidebar:
    *   Select the model type (Epistemic Bubble or Echo Chamber).
    *   Set the number of agents and connection probability.
    *   Choose the initial belief distribution (e.g., 'bimodal' often shows polarization effects).
    *   Adjust the belief update step size and interaction chance.
    *   If using the Echo Chamber model, configure trust-related parameters (threshold, default trust, initial setup).
2.  **Setup/Reset:** Click the "Setup / Reset Simulation" button to initialize the simulation with the current parameters.
3.  **Start/Resume:** Click "Start / Resume" to run the simulation step-by-step. The visualization will update automatically.
4.  **Pause:** Click "Pause" to halt the simulation while keeping the current state.
5.  **Visualization:** The main panel shows the network graph. Nodes represent agents, and their color indicates their belief state (e.g., blue towards 0, red towards 1). Edges show connections.

## Potential Extensions

*   Implement more sophisticated network structures (e.g., scale-free, small-world, community structures).
*   Add dynamic trust updates in the Echo Chamber model.
*   Visualize trust relationships in the Echo Chamber model.
*   Introduce different types of information or topics.
*   Add more complex agent behaviors (e.g., selective exposure based on belief).
*   Include metrics and plots to track polarization, average belief, etc., over time. 