import networkx as nx
import random

def create_group_aware_network(agents_dict, p_intra, p_inter):
    """
    Creates a network with different connection probabilities within and between groups.

    Args:
        agents_dict (dict): Dictionary of {agent_id: Agent object}. 
                          Agents must have a 'group' attribute ('A' or 'B').
        p_intra (float): Probability of connection between agents in the same group.
        p_inter (float): Probability of connection between agents in different groups.

    Returns:
        networkx.Graph: The generated network graph.
    """
    G = nx.Graph()
    agent_ids = list(agents_dict.keys())
    G.add_nodes_from(agent_ids)

    agent_list = list(agents_dict.values()) # For easier iteration

    for i in range(len(agent_list)):
        for j in range(i + 1, len(agent_list)):
            agent_i = agent_list[i]
            agent_j = agent_list[j]

            # Determine connection probability based on groups
            if agent_i.group == agent_j.group:
                # Intra-group connection
                connection_probability = p_intra
            else:
                # Inter-group connection
                connection_probability = p_inter
            
            # Add edge based on the determined probability
            if random.random() < connection_probability:
                G.add_edge(agent_i.id, agent_j.id)
                
    return G

# --- Helper function from pseudocode (adapted for networkx) ---
def get_neighbors(network, agent_id):
    """Gets the neighbors of an agent from the networkx graph."""
    if agent_id in network:
        return list(network.neighbors(agent_id))
    return [] 