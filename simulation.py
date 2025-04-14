import random
import networkx as nx
from agent import Agent
from network_utils import create_group_aware_network
from models import receive_message_bubble, receive_message_chamber
import numpy as np # For metrics calculation
# from scipy.stats import kurtosis # No longer needed

class Simulation:
    """Manages the simulation state and execution."""
    def __init__(self, params):
        """
        Initializes the simulation environment.

        Args:
            params (dict): A dictionary containing simulation parameters like:
                num_agents (int)
                model_type ('bubble' or 'chamber')
                connection_probability_intra (float)
                connection_probability_inter (float)
                initial_belief_distribution ('uniform', 'random', 'bimodal')
                belief_update_step_size (float)
                trust_threshold (float, for chamber)
                default_outsider_trust (float, for chamber)
                interaction_chance (float)
                initial_trust_setup ('uniform_high', 'belief_based', for chamber)
                step_delay (float)
        """
        self.params = params
        self.agents = {} # Dictionary {agent_id: Agent object}
        self.network = None
        self.receive_message_func = None
        self.time_step = 0

        self._setup_simulation()

    def _setup_simulation(self):
        """Sets up the agents and network based on initial parameters."""
        # Create Agents
        agent_ids = list(range(self.params['num_agents']))
        for agent_id in agent_ids:
            initial_belief = self._get_initial_belief()
            self.agents[agent_id] = Agent(agent_id, initial_belief)

        # Create Network
        self.network = create_group_aware_network(
            self.agents,
            self.params['connection_probability_intra'],
            self.params['connection_probability_inter']
        )

        # Assign connections to Agents and initialize trust (if chamber)
        for agent_id in self.agents:
            agent = self.agents[agent_id]
            neighbors = list(self.network.neighbors(agent_id))
            agent.connections = set(neighbors)

            if self.params['model_type'] == 'chamber':
                trust_scores = self._initialize_trust(agent, agent_ids)
                agent.set_trust_scores(trust_scores)

        # Select the correct message handling function
        if self.params['model_type'] == 'bubble':
            self.receive_message_func = receive_message_bubble
        elif self.params['model_type'] == 'chamber':
            self.receive_message_func = receive_message_chamber
        else:
            raise ValueError(f"Unknown model type: {self.params['model_type']}")

    def _get_initial_belief(self):
        """Determines the initial belief for an agent based on distribution type."""
        dist_type = self.params.get('initial_belief_distribution', 'random')
        if dist_type == 'uniform':
            # Placeholder for uniform - let's use random for now
            return random.random()
        elif dist_type == 'bimodal':
            # Simple bimodal: half near 0, half near 1
            return random.choice([random.uniform(0, 0.2), random.uniform(0.8, 1.0)])
        elif dist_type == 'random':
            return random.random() # Default: random between 0 and 1
        else:
            print(f"Warning: Unknown initial_belief_distribution '{dist_type}'. Using random.")
            return random.random()

    def _initialize_trust(self, agent, all_agent_ids):
        """Initializes trust scores for an agent in the Echo Chamber model."""
        setup_type = self.params.get('initial_trust_setup', 'uniform_high')
        trust_scores = {}
        default_trust = self.params.get('default_outsider_trust', 0.1)
        high_trust_value = 0.9 # Example value for high trust

        if setup_type == 'uniform_high':
            for other_id in all_agent_ids:
                if other_id != agent.id:
                    trust_scores[other_id] = high_trust_value
        elif setup_type == 'belief_based':
             # Trust others more if their initial belief is similar
             belief_similarity_threshold = 0.3 # Example threshold
             for other_id in all_agent_ids:
                 if other_id != agent.id:
                     other_agent = self.agents[other_id]
                     if abs(agent.belief_state - other_agent.belief_state) < belief_similarity_threshold:
                         trust_scores[other_id] = high_trust_value
                     else:
                         trust_scores[other_id] = default_trust # Lower trust if belief differs
        else:
            print(f"Warning: Unknown initial_trust_setup '{setup_type}'. Using uniform_high.")
            for other_id in all_agent_ids:
                if other_id != agent.id:
                    trust_scores[other_id] = high_trust_value

        return trust_scores

    def simulation_step(self):
        """Executes one step of the simulation where each agent interacts."""
        if not self.agents:
            return # No agents to process

        # --- Agent Interaction Logic (Modified) ---
        # Process agents in a random order to avoid bias
        agent_ids_to_process = list(self.agents.keys())
        random.shuffle(agent_ids_to_process)

        interaction_count = 0
        for agent_id in agent_ids_to_process:
            acting_agent = self.agents[agent_id]

            # Check if interaction occurs based on chance (per agent)
            if random.random() < self.params.get('interaction_chance', 0.5):
                neighbors = list(acting_agent.connections)
                if neighbors:
                    # Choose a random neighbor to interact with
                    recipient_agent_id = random.choice(neighbors)
                    recipient_agent = self.agents[recipient_agent_id]

                    # Message content is simply the sender's current belief state
                    message_content = acting_agent.belief_state

                    # Send the message (call the appropriate receive function)
                    self.send_message(recipient_agent, message_content, acting_agent)
                    interaction_count += 1

        self.time_step += 1
        # print(f"Step {self.time_step}: {interaction_count} interactions occurred.") # Optional debug print

    def send_message(self, recipient_agent, message_content, sender_agent):
        """
        Handles the delivery of a message using the model-specific logic.
        Passes necessary simulation parameters to the handling function.
        """
        if self.receive_message_func:
            # Pass relevant parameters from self.params using **kwargs
            # This avoids needing to change function signatures in models.py
            # if we add more parameters later.
            handler_params = {
                'belief_update_step_size': self.params.get('belief_update_step_size', 0.1),
                'trust_threshold': self.params.get('trust_threshold', 0.5),
                'default_outsider_trust': self.params.get('default_outsider_trust', 0.1)
            }
            self.receive_message_func(
                recipient_agent, message_content, sender_agent, **handler_params
            )

    def calculate_metrics(self):
        """Calculates metrics about the current simulation state, using fixed agent groups."""
        if not self.agents:
            return {
                'avg_belief': None, 'std_dev_belief': None,
                'group_A_count': 0, 'group_A_avg': None, 'group_A_std': None,
                'group_B_count': 0, 'group_B_avg': None, 'group_B_std': None,
            }

        # Separate agents by their fixed group attribute
        group_A_agents = [agent for agent in self.agents.values() if agent.group == 'A']
        group_B_agents = [agent for agent in self.agents.values() if agent.group == 'B']

        # Extract beliefs for calculation
        all_beliefs = np.array([agent.belief_state for agent in self.agents.values()])
        group_A_beliefs = np.array([agent.belief_state for agent in group_A_agents])
        group_B_beliefs = np.array([agent.belief_state for agent in group_B_agents])

        metrics = {
            'avg_belief': np.mean(all_beliefs) if all_beliefs.size > 0 else None,
            'std_dev_belief': np.std(all_beliefs) if all_beliefs.size > 0 else None,
            
            'group_A_count': len(group_A_agents),
            'group_A_avg': np.mean(group_A_beliefs) if group_A_beliefs.size > 0 else None,
            'group_A_std': np.std(group_A_beliefs) if group_A_beliefs.size > 1 else 0,

            'group_B_count': len(group_B_agents),
            'group_B_avg': np.mean(group_B_beliefs) if group_B_beliefs.size > 0 else None,
            'group_B_std': np.std(group_B_beliefs) if group_B_beliefs.size > 1 else 0,
        }
        
        return metrics

    def get_simulation_state(self):
         """Returns the current state needed for visualization."""
         return {
             'agents': self.agents,
             'network': self.network,
             'time_step': self.time_step,
             'model_type': self.params.get('model_type')
         } 