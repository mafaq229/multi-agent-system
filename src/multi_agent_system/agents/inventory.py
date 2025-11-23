"""
Inventory & Procurement Agent.

Responsible for:
- Checking inventory levels
- Determining reorder needs
- Calculating supplier delivery times
- Managing stock thresholds
"""

from datetime import datetime
from typing import Any, Dict

from multi_agent_system.agents.base import BaseAgent
from multi_agent_system.agents.prompts.inventory_prompts import INVENTORY_SYSTEM_PROMPT
from multi_agent_system.services.inventory_service import InventoryService


class InventoryAgent(BaseAgent):
    """
    Inventory & Procurement Agent.

    Responsibilities:
    - Check current inventory levels
    - Determine if reordering is needed
    - Calculate supplier delivery times
    - Provide availability information
    """

    def __init__(
        self,
        inventory_service: InventoryService,
        model: str = "openai:gpt-4o-mini",
        **kwargs
    ):
        """
        Initialize inventory agent.

        Args:
            inventory_service: Service for inventory operations
            model: Model identifier for the AI agent
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="inventory",
            model=model,
            system_prompt=INVENTORY_SYSTEM_PROMPT,
            **kwargs
        )
        self.inventory_service = inventory_service
        self._register_tools()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inventory check request.

        Args:
            input_data: Dictionary with:
                - item_name: Name of item to check
                - quantity: Requested quantity
                - request_date: Date for availability check

        Returns:
            Dictionary with inventory status and availability info
        """
        self._log_start(input_data)
        try:
            item_name = input_data["item_name"]
            quantity = input_data["quantity"]
            request_date = input_data.get("request_date", datetime.now())  # noqa: DTZ005

            if isinstance(request_date, str):
                request_date = datetime.fromisoformat(request_date)

            result = self.inventory_service.check_availability(
                item_name=item_name,
                quantity=quantity,
                as_of_date=request_date
            )

            response = {
                "item_name": result.item_name,
                "current_stock": result.current_stock,
                "requested_quantity": result.requested_quantity,
                "available": result.available,
                "shortage": result.shortage,
                "needs_reorder": result.needs_reorder,
                "reorder_quantity": result.reorder_quantity,
                "supplier_eta": result.supplier_eta.isoformat() if result.supplier_eta else None,
                "success": True
            }

            self._log_complete(response)
            return response

        except Exception as e:
            return self._handle_error(e)

    def _register_tools(self) -> None:
        """Register agent tools for inventory operations."""

        @self._agent.tool
        def check_inventory(item_name: str, quantity: int, request_date: str | None = None) -> Dict[str, Any]:
            """
            Check inventory availability for an item.

            Args:
                item_name: Name of the item to check
                quantity: Quantity needed
                request_date: Optional date for the check (ISO format)

            Returns:
                Dictionary with availability information
            """
            date = datetime.fromisoformat(request_date) if request_date else datetime.now()  # noqa: DTZ005
            result = self.inventory_service.check_availability(
                item_name=item_name,
                quantity=quantity,
                as_of_date=date
            )
            return {
                "item_name": result.item_name,
                "current_stock": result.current_stock,
                "available": result.available,
                "shortage": result.shortage,
                "needs_reorder": result.needs_reorder,
                "reorder_quantity": result.reorder_quantity,
                "supplier_eta": result.supplier_eta.isoformat() if result.supplier_eta else None
            }

        @self._agent.tool
        def get_available_inventory(request_date: str | None = None) -> Dict[str, int]:
            """
            Get all available inventory as of a specific date.

            Args:
                request_date: Optional date for inventory snapshot (ISO format)

            Returns:
                Dictionary mapping item names to stock levels
            """
            date = datetime.fromisoformat(request_date) if request_date else datetime.now()  # noqa: DTZ005
            return self.inventory_service.get_all_inventory(as_of_date=date)

        @self._agent.tool
        def calculate_reorder_quantity(item_name: str) -> int:
            """
            Calculate recommended reorder quantity for an item.

            Args:
                item_name: Name of the item

            Returns:
                Recommended reorder quantity
            """
            return self.inventory_service.calculate_reorder_quantity(item_name)

        @self._agent.tool
        def get_supplier_eta(quantity: int, request_date: str | None = None) -> str:
            """
            Get estimated supplier delivery date for a given quantity.

            Args:
                quantity: Order quantity
                request_date: Optional request date (ISO format)

            Returns:
                Estimated delivery date in ISO format
            """
            date = datetime.fromisoformat(request_date) if request_date else datetime.now()  # noqa: DTZ005
            eta = self.inventory_service.get_supplier_delivery_date(quantity, date)
            return eta.isoformat()

        @self._agent.tool
        def get_low_stock_items() -> list[Dict[str, Any]]:
            """
            Get items that are at or below minimum stock level.

            Returns:
                List of low stock items with details
            """
            items = self.inventory_service.get_low_stock_items()
            return [
                {
                    "item_name": item.item_name,
                    "category": item.category.value,
                    "current_stock": item.current_stock,
                    "min_stock_level": item.min_stock_level,
                    "unit_price": item.unit_price
                }
                for item in items
            ]

