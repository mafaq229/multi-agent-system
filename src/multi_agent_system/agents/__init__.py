"""Multi-agent system with specialized agents."""

from multi_agent_system.agents.base import AgentProtocol, BaseAgent, create_agent, validate_agent_response
from multi_agent_system.agents.fulfillment import FulfillmentAgent
from multi_agent_system.agents.inventory import InventoryAgent
from multi_agent_system.agents.orchestrator import OrchestratorAgent
from multi_agent_system.agents.quoting import QuotingAgent

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentProtocol",
    # Specialized agents
    "InventoryAgent",
    "QuotingAgent",
    "FulfillmentAgent",
    "OrchestratorAgent",
    # Utility functions
    "create_agent",
    "validate_agent_response",
]

