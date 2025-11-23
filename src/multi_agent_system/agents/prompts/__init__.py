"""Agent system prompts."""

from multi_agent_system.agents.prompts.fulfillment_prompts import (
    BACKORDER_MANAGEMENT_PROMPT,
    FULFILLMENT_SYSTEM_PROMPT,
    ORDER_ALLOCATION_PROMPT,
)
from multi_agent_system.agents.prompts.inventory_prompts import (
    INVENTORY_SYSTEM_PROMPT,
    REORDER_RECOMMENDATION_PROMPT,
    REQUEST_PARSING_PROMPT as INVENTORY_REQUEST_PARSING_PROMPT,
)
from multi_agent_system.agents.prompts.orchestrator_prompts import (
    ERROR_HANDLING_PROMPT,
    ORCHESTRATOR_SYSTEM_PROMPT,
    REQUEST_PARSING_PROMPT,
    RESPONSE_FORMATTING_PROMPT,
)
from multi_agent_system.agents.prompts.quoting_prompts import (
    HISTORICAL_QUOTE_SEARCH_PROMPT,
    PRICING_ANALYSIS_PROMPT,
    QUOTING_SYSTEM_PROMPT,
)

__all__ = [
    # Orchestrator
    "ORCHESTRATOR_SYSTEM_PROMPT",
    "REQUEST_PARSING_PROMPT",
    "ERROR_HANDLING_PROMPT",
    "RESPONSE_FORMATTING_PROMPT",
    # Inventory
    "INVENTORY_SYSTEM_PROMPT",
    "INVENTORY_REQUEST_PARSING_PROMPT",
    "REORDER_RECOMMENDATION_PROMPT",
    # Quoting
    "QUOTING_SYSTEM_PROMPT",
    "PRICING_ANALYSIS_PROMPT",
    "HISTORICAL_QUOTE_SEARCH_PROMPT",
    # Fulfillment
    "FULFILLMENT_SYSTEM_PROMPT",
    "ORDER_ALLOCATION_PROMPT",
    "BACKORDER_MANAGEMENT_PROMPT",
]
