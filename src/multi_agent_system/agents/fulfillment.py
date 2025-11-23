"""Fulfillment Agent - Process orders and manage inventory allocation."""

from datetime import datetime
from typing import Any, Dict

from multi_agent_system.agents.base import BaseAgent
from multi_agent_system.agents.prompts.fulfillment_prompts import FULFILLMENT_SYSTEM_PROMPT
from multi_agent_system.domain.models import QuoteItemRequest
from multi_agent_system.services.fulfillment_service import FulfillmentService


class FulfillmentAgent(BaseAgent):
    """
    Fulfillment Agent for order processing.

    Responsibilities:
    - Process orders
    - Allocate inventory
    - Handle backorders
    - Record transactions
    """

    def __init__(
        self,
        fulfillment_service: FulfillmentService,
        model: str = "openai:gpt-4o-mini",
        **kwargs
    ):
        """
        Initialize fulfillment agent.

        Args:
            fulfillment_service: Service for fulfillment operations
            model: Model identifier for the AI agent
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="fulfillment",
            model=model,
            system_prompt=FULFILLMENT_SYSTEM_PROMPT,
            **kwargs
        )
        self.fulfillment_service = fulfillment_service
        self._register_tools()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process order fulfillment request.

        Args:
            input_data: Dictionary with:
                - items: List of items with quantities
                - customer_id: Customer identifier
                - request_date: Date of request
                - quote_id: Optional associated quote ID

        Returns:
            Dictionary with order fulfillment details
        """
        self._log_start(input_data)
        try:
            items = input_data["items"]
            customer_id = input_data.get("customer_id", "UNKNOWN")
            request_date = input_data.get("request_date", datetime.now())  # noqa: DTZ005
            quote_id = input_data.get("quote_id")

            if isinstance(request_date, str):
                request_date = datetime.fromisoformat(request_date)

            # Convert items to QuoteItemRequest objects
            order_items = []
            for item in items:
                if isinstance(item, dict):
                    order_items.append(
                        QuoteItemRequest(
                            item_name=item["item_name"],
                            quantity=item["quantity"]
                        )
                    )
                else:
                    order_items.append(item)

            order = self.fulfillment_service.process_order(
                items=order_items,
                customer_id=customer_id,
                request_date=request_date,
                quote_id=quote_id
            )

            response = {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "quote_id": order.quote_id,
                "status": order.status.value,
                "items_fulfilled": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.subtotal
                    }
                    for item in order.items_fulfilled
                ],
                "backorder_items": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity
                    }
                    for item in order.backorder_items
                ],
                "total_amount": order.total_amount,
                "delivery_date": order.delivery_date.isoformat(),
                "tracking_number": order.tracking_number,
                "success": True
            }

            self._log_complete(response)
            return response

        except Exception as e:
            return self._handle_error(e)

    def _register_tools(self) -> None:
        """Register agent tools for fulfillment operations."""

        @self._agent.tool
        def fulfill_order(
            items: list[Dict[str, Any]],
            customer_id: str,
            request_date: str | None = None,
            quote_id: str | None = None
        ) -> Dict[str, Any]:
            """
            Process and fulfill an order.

            Args:
                items: List of dictionaries with item_name and quantity
                customer_id: Customer identifier
                request_date: Optional date of request (ISO format)
                quote_id: Optional associated quote ID

            Returns:
                Dictionary with order fulfillment details
            """
            date = datetime.fromisoformat(request_date) if request_date else datetime.now()  # noqa: DTZ005

            order_items = [
                QuoteItemRequest(item_name=item["item_name"], quantity=item["quantity"])
                for item in items
            ]

            order = self.fulfillment_service.process_order(
                items=order_items,
                customer_id=customer_id,
                request_date=date,
                quote_id=quote_id
            )

            return {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "quote_id": order.quote_id,
                "status": order.status.value,
                "items_fulfilled": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.subtotal
                    }
                    for item in order.items_fulfilled
                ],
                "backorder_items": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity
                    }
                    for item in order.backorder_items
                ],
                "total_amount": order.total_amount,
                "delivery_date": order.delivery_date.isoformat(),
                "tracking_number": order.tracking_number
            }

        @self._agent.tool
        def allocate_inventory(items: list[Dict[str, Any]]) -> Dict[str, int]:
            """
            Allocate inventory for order items.

            Args:
                items: List of dictionaries with item_name and quantity

            Returns:
                Dictionary mapping item names to allocated quantities
            """
            order_items = [
                QuoteItemRequest(item_name=item["item_name"], quantity=item["quantity"])
                for item in items
            ]

            return self.fulfillment_service.allocate_inventory(order_items)

        @self._agent.tool
        def create_backorder(
            item_name: str,
            quantity: int,
            expected_date: str | None = None
        ) -> Dict[str, Any]:
            """
            Create a backorder for an item.

            Args:
                item_name: Name of the item
                quantity: Quantity on backorder
                expected_date: Optional expected fulfillment date (ISO format)

            Returns:
                Dictionary with backorder information
            """
            exp_date = datetime.fromisoformat(expected_date) if expected_date else None

            backorder = self.fulfillment_service.create_backorder(
                item_name=item_name,
                quantity=quantity,
                expected_date=exp_date
            )

            # Convert datetime to string for JSON serialization
            if isinstance(backorder.get("expected_date"), datetime):
                backorder["expected_date"] = backorder["expected_date"].isoformat()

            return backorder

        @self._agent.tool
        def record_transaction(
            item_name: str,
            quantity: int,
            price: float,
            transaction_date: str | None = None
        ) -> int:
            """
            Record a sale transaction.

            Args:
                item_name: Name of the item
                quantity: Quantity sold
                price: Total sale price
                transaction_date: Optional transaction date (ISO format)

            Returns:
                Transaction ID
            """
            date = datetime.fromisoformat(transaction_date) if transaction_date else datetime.now()  # noqa: DTZ005

            return self.fulfillment_service.record_sale_transaction(
                item_name=item_name,
                quantity=quantity,
                price=price,
                transaction_date=date
            )

        @self._agent.tool
        def trigger_reorder(item_name: str, quantity: int) -> None:
            """
            Trigger a reorder for an item.

            Args:
                item_name: Name of the item
                quantity: Quantity to reorder
            """
            self.fulfillment_service.trigger_reorder(item_name, quantity)

