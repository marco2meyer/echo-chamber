from agent import Agent
import random

# --- Helper function for simple belief update (from pseudocode) ---
def update_belief_simple(current_belief, message_content, step_size=0.1):
    """
    Updates belief based on message content by moving slightly towards it.

    Args:
        current_belief (float): The agent's current belief state (0 to 1).
        message_content (float): The belief expressed in the message (0 to 1).
        step_size (float): How much belief shifts per message.

    Returns:
        float: The updated belief state.
    """
    if message_content > current_belief:
        # Ensure belief stays <= 1.0
        return min(1.0, current_belief + step_size)
    elif message_content < current_belief:
        # Ensure belief stays >= 0.0
        return max(0.0, current_belief - step_size)
    else:
        return current_belief # No change if message matches belief

# --- Message Handling for Model B (Epistemic Bubble) ---
def receive_message_bubble(recipient_agent: Agent, message_content: float, sender_agent: Agent, **kwargs):
    """
    Processes a received message according to the Epistemic Bubble model.
    Belief update happens simply based on content, as omission is handled
    by the network structure (only connected agents send messages).

    Args:
        recipient_agent (Agent): The agent receiving the message.
        message_content (float): The belief content of the message.
        sender_agent (Agent): The agent sending the message.
        **kwargs: Catches potential extra arguments like step_size.
    """
    step_size = kwargs.get('belief_update_step_size', 0.1) # Use provided step size or default

    # The core idea of the bubble is omission - if the message is received,
    # it means the sender *is* connected. The agent updates based on content.
    # An explicit check 'sender_agent.id in recipient_agent.connections' is redundant
    # if the simulation loop only sends messages between connected agents.
    new_belief = update_belief_simple(recipient_agent.belief_state, message_content, step_size)
    recipient_agent.update_belief(new_belief) # Use agent's method to handle bounds

# --- Message Handling for Model C (Echo Chamber) ---
def receive_message_chamber(recipient_agent: Agent, message_content: float, sender_agent: Agent, **kwargs):
    """
    Processes a received message according to the Echo Chamber model.
    Belief update depends on the recipient's trust score for the sender.

    Args:
        recipient_agent (Agent): The agent receiving the message.
        message_content (float): The belief content of the message.
        sender_agent (Agent): The agent sending the message.
        **kwargs: Catches potential extra arguments like trust_threshold, step_size, default_trust.
    """
    trust_threshold = kwargs.get('trust_threshold', 0.5)
    default_trust = kwargs.get('default_outsider_trust', 0.1)
    step_size = kwargs.get('belief_update_step_size', 0.1)

    # Get the trust score for the sender from the recipient's perspective
    sender_trust = recipient_agent.get_trust_score(sender_agent.id, default_trust=default_trust)

    if sender_trust >= trust_threshold:
        # Sender is trusted: Update belief based on message content
        new_belief = update_belief_simple(recipient_agent.belief_state, message_content, step_size)
        recipient_agent.update_belief(new_belief)
        # Optional: Implement trust reinforcement here if desired
        # update_trust(recipient_agent, sender_agent, "confirming")
    else:
        # Sender is distrusted: Ignore the message (active discrediting)
        pass
        # Optional: Implement belief update away from the message or trust decrease
        # update_trust(recipient_agent, sender_agent, "disconfirming")

# --- Placeholder for optional trust update logic ---
# def update_trust(agent, sender, message_type):
#     # Logic for how trust changes based on interactions
#     # e.g., increase trust if sender is already trusted and sends confirming message
#     # e.g., decrease trust if sender is distrusted or sends disconfirming message
#     pass 