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

*   `simulation.py`: Contains the `Simulation` class (core engine).
*   `agent.py`: Defines the `Agent` class.
*   `models.py`: Implements the belief update logic (Bubble vs. Chamber).
*   `network_utils.py`: Contains network generation logic.
*   `visualization.py`: Contains functions to generate Plotly figures for network and metrics (UI-agnostic).
*   `streamlit_app.py`: The Streamlit front-end application.
*   `dash_app.py`: The Dash front-end application.
*   `requirements.txt`: Lists the necessary Python libraries.
*   `README.md`: This file.

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
4.  **Run the desired application:**
    *   **To run the Streamlit version:**
        ```bash
        streamlit run streamlit_app.py
        ```
    *   **To run the Dash version:**
        ```bash
        python dash_app.py
        ```
        Then, open your web browser and navigate to `http://127.0.0.1:8050/` (or the address indicated in the terminal).

## Using the Applications

Both applications provide similar controls in the sidebar for adjusting simulation parameters. 

*   **Streamlit App:** Uses `st.rerun` for updates, which may cause some visual flickering during simulation steps.
*   **Dash App:** Uses callbacks and targeted updates, resulting in smoother visualization updates without full page redraws.

Use the **Setup / Reset**, **Start / Resume**, and **Pause** buttons to control the simulation in both versions.

## Potential Extensions

*   Implement more sophisticated network structures (e.g., scale-free, small-world, community structures).
*   Add dynamic trust updates in the Echo Chamber model.
*   Visualize trust relationships in the Echo Chamber model.
*   Introduce different types of information or topics.
*   Add more complex agent behaviors (e.g., selective exposure based on belief).
*   Include metrics and plots to track polarization, average belief, etc., over time. 