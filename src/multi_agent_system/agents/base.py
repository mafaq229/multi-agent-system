"""
Base agent protocol and abstract class.

This module defines the interface that all agents must implement,
ensuring consistent agent behavior across the system.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Protocol

from pydantic_ai import Agent

from multi_agent_system.core.logging import get_logger


class AgentProtocol(Protocol):
    """
    Protocol defining the interface for all agents.

    This ensures type safety and consistent agent behavior.
    """

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process input and return result.

        Args:
            input_data: Input data for the agent

        Returns:
            Processing result
        """
        ...


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Provides common functionality for:
    - Initialization
    - Logging
    - Error handling
    - State management
    - Tool registration
    """

    def __init__(
        self,
        name: str,
        model: str,
        system_prompt: str,
        logger: Any | None = None
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name (e.g., "inventory", "quoting")
            model: Model identifier (e.g., "openai:gpt-4o-mini")
            system_prompt: System prompt defining agent behavior
            logger: Optional logger instance (creates one if not provided)
        """
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.logger = logger or get_logger(f"agent.{name}")
        self._agent = Agent(model, system_prompt=system_prompt)

    @abstractmethod
    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process input data and return result.

        This method must be implemented by subclasses to define
        specific agent behavior.

        Args:
            input_data: Input data for processing

        Returns:
            Processing result

        Raises:
            AgentError: If processing fails
        """

    def register_tool(self, tool_func: Callable) -> None:
        """
        Register a tool with the agent.

        Args:
            tool_func: Function to register as a tool
        """
        self._agent.tool(tool_func)

    def _log_start(self, input_data: dict[str, Any]) -> None:
        """
        Log agent processing start.

        Args:
            input_data: Input data being processed
        """
        self.logger.info(
            "Agent processing started",
            agent=self.name,
            input_keys=list(input_data.keys())
        )

    def _log_complete(self, result: dict[str, Any]) -> None:
        """
        Log agent processing completion.

        Args:
            result: Processing result
        """
        self.logger.info(
            "Agent processing completed",
            agent=self.name,
            result_keys=list(result.keys())
        )

    def _handle_error(self, error: Exception) -> dict[str, Any]:
        """
        Handle agent errors consistently.

        Args:
            error: Exception that occurred

        Returns:
            Error response dictionary
        """
        self.logger.exception(
            "Agent processing failed",
            agent=self.name,
            error=str(error)
        )
        return {
            "error": str(error),
            "agent": self.name,
            "success": False
        }


def create_agent(agent_type: str, config: dict[str, Any]) -> BaseAgent:
    """
    Factory function to create agents by type.

    Args:
        agent_type: Type of agent to create
        config: Configuration dictionary for the agent

    Returns:
        Configured agent instance

    Raises:
        ValueError: If agent_type is not recognized
    """
    from multi_agent_system.agents.fulfillment import FulfillmentAgent
    from multi_agent_system.agents.inventory import InventoryAgent
    from multi_agent_system.agents.orchestrator import OrchestratorAgent
    from multi_agent_system.agents.quoting import QuotingAgent

    agent_classes: dict[str, type[BaseAgent]] = {
        "inventory": InventoryAgent,
        "quoting": QuotingAgent,
        "fulfillment": FulfillmentAgent,
        "orchestrator": OrchestratorAgent,
    }

    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        error_msg = f"Unknown agent type: {agent_type}"
        raise ValueError(error_msg)

    return agent_class(**config)


def validate_agent_response(response: dict[str, Any]) -> bool:
    """
    Validate that an agent response has the expected structure.

    Args:
        response: Agent response dictionary

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(response, dict):
        return False

    # Check for error response
    if "error" in response:
        return "agent" in response and "success" in response

    # Valid responses should have at least some data
    return bool(response)

