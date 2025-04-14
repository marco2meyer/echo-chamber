import random

class Agent:
    """Represents an agent in the simulation."""
    def __init__(self, agent_id, initial_belief, connections=None, trust_scores=None):
        """
        Initializes an agent.

        Args:
            agent_id (int): Unique identifier for the agent.
            initial_belief (float): Agent's starting belief (e.g., 0 to 1).
            connections (list, optional): List of agent IDs this agent is connected to. Defaults to None.
            trust_scores (dict, optional): Map {agent_id -> trust_score} for Echo Chamber model. Defaults to None.
        """
        self.id = agent_id
        self.belief_state = initial_belief
        # --- Assign Fixed Group based on initial belief --- 
        self.group = 'A' if initial_belief < 0.5 else 'B'
        # --- End Group Assignment ---
        # Store connections as a set for efficient lookup
        self.connections = set(connections) if connections else set()
        # Trust scores specific to Echo Chamber model
        self.trust_scores = trust_scores if trust_scores else {}

    def add_connection(self, other_agent_id):
        """Adds a connection to another agent."""
        self.connections.add(other_agent_id)

    def set_trust_scores(self, scores):
        """Sets the trust scores for this agent."""
        self.trust_scores = scores

    def get_trust_score(self, other_agent_id, default_trust=0.1):
        """
        Retrieves the trust score for a specific agent.

        Args:
            other_agent_id (int): The ID of the agent whose trust score is needed.
            default_trust (float): The trust score to return if the agent is not explicitly listed.

        Returns:
            float: The trust score.
        """
        return self.trust_scores.get(other_agent_id, default_trust)

    def __repr__(self):
        # Include group in representation
        return f"Agent(id={self.id}, group={self.group}, belief={self.belief_state:.2f}, connections={len(self.connections)})"

    def update_belief(self, new_belief):
         """Updates the agent's belief state, ensuring it stays within [0, 1]."""
         self.belief_state = max(0.0, min(1.0, new_belief))    