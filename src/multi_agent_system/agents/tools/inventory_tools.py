"""Tools for inventory agent operations."""

# NOTE: Tools are now registered directly within the InventoryAgent class
# using the @self._agent.tool decorator pattern from pydantic-ai.
#
# This file is kept for potential future shared tools that might be used
# across multiple agents.
#
# See: src/multi_agent_system/agents/inventory.py for tool implementations:
# - check_inventory(item_name, quantity, request_date)
# - get_available_inventory(request_date)
# - calculate_reorder_quantity(item_name)
# - get_supplier_eta(quantity, request_date)
# - get_low_stock_items()

