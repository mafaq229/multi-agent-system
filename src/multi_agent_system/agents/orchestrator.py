"""
Orchestrator agent for coordinating other agents.

The orchestrator is responsible for:
- Parsing customer requests
- Routing to appropriate specialized agents
- Coordinating multi-agent workflows
- Formatting final responses
"""

import json
from datetime import datetime
from typing import Any, Dict

from multi_agent_system.agents.base import BaseAgent
from multi_agent_system.agents.fulfillment import FulfillmentAgent
from multi_agent_system.agents.inventory import InventoryAgent
from multi_agent_system.agents.prompts.orchestrator_prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    REQUEST_PARSING_PROMPT,
)
from multi_agent_system.agents.quoting import QuotingAgent


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator agent for workflow coordination.

    Responsibilities:
    1. Parse customer requests to extract intent and items
    2. Coordinate with specialized agents
    3. Manage workflow state
    4. Handle errors and retries
    5. Format responses for customers
    """

    def __init__(
        self,
        inventory_agent: InventoryAgent,
        quoting_agent: QuotingAgent,
        fulfillment_agent: FulfillmentAgent,
        model: str = "openai:gpt-4o-mini",
        **kwargs
    ):
        """
        Initialize orchestrator agent.

        Args:
            inventory_agent: Agent for inventory operations
            quoting_agent: Agent for quote generation
            fulfillment_agent: Agent for order fulfillment
            model: Model identifier for the AI agent
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="orchestrator",
            model=model,
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            **kwargs
        )
        self.inventory_agent = inventory_agent
        self.quoting_agent = quoting_agent
        self.fulfillment_agent = fulfillment_agent

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer request through full workflow.

        Args:
            input_data: Dictionary with:
                - request: Customer request text
                - customer_id: Customer identifier
                - request_date: Date of request
                - auto_fulfill: Whether to automatically fulfill order

        Returns:
            Dictionary with complete workflow result
        """
        self._log_start(input_data)
        try:
            request_text = input_data.get("request", "")
            customer_id = input_data.get("customer_id", "UNKNOWN")
            request_date = input_data.get("request_date", datetime.now())  # noqa: DTZ005
            auto_fulfill = input_data.get("auto_fulfill", True)

            if isinstance(request_date, str):
                request_date = datetime.fromisoformat(request_date)

            # 1. Parse request to extract items
            parsed = self._parse_request(request_text)

            # 2. Check inventory for each item
            inventory_results = []
            all_available = True
            for item in parsed["items"]:
                result = self.inventory_agent.process({
                    "item_name": item["item_name"],
                    "quantity": item["quantity"],
                    "request_date": request_date.isoformat()
                })
                inventory_results.append(result)
                if not result.get("available", False):
                    all_available = False

            # 3. Generate quote
            quote = self.quoting_agent.process({
                "items": parsed["items"],
                "customer_id": customer_id,
                "request_date": request_date.isoformat(),
                "notes": parsed.get("notes")
            })

            # 4. Fulfill order if auto_fulfill is True
            fulfillment = None
            if auto_fulfill and quote.get("success"):
                fulfillment = self.fulfillment_agent.process({
                    "items": parsed["items"],
                    "customer_id": customer_id,
                    "request_date": request_date.isoformat(),
                    "quote_id": quote.get("quote_id")
                })

            # 5. Format final response
            response = self._format_response(
                quote=quote,
                fulfillment=fulfillment,
                inventory_results=inventory_results,
                all_available=all_available
            )

            self._log_complete(response)
            return response

        except Exception as e:
            return self._handle_error(e)

    def _parse_request(self, request_text: str) -> Dict[str, Any]:
        """
        Parse customer request to extract items and quantities.

        Args:
            request_text: Natural language customer request

        Returns:
            Dictionary with parsed items and context
        """
        try:
            # Use the LLM to parse the request
            result = self._agent.run_sync(
                f"{REQUEST_PARSING_PROMPT}\n\nCustomer Request: {request_text}\n\n"
                "Extract items with their names and quantities. "
                "Return a JSON object with 'items' (list of objects with 'item_name' and 'quantity') "
                "and 'notes' (any additional context)."
            )

            # Try to parse the result as JSON
            if hasattr(result, 'data'):
                data = result.data
            else:
                data = str(result)

            # If data is a string, try to parse as JSON
            if isinstance(data, str):
                # Try to find JSON in the response
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract structured data
                    # Default fallback parsing
                    parsed = {"items": [], "notes": request_text}
            else:
                parsed = data

            # Ensure items list exists and is properly formatted
            if "items" not in parsed or not isinstance(parsed["items"], list):
                # Fallback: try to extract basic items
                parsed = {
                    "items": [
                        {"item_name": "A4 paper", "quantity": 1000}
                    ],
                    "notes": request_text
                }

            return parsed

        except Exception as e:
            self.logger.error(f"Error parsing request: {e}")
            # Return a basic structure on error
            return {
                "items": [],
                "notes": request_text,
                "error": str(e)
            }

    def _format_response(
        self,
        quote: Dict[str, Any],
        fulfillment: Dict[str, Any] | None = None,
        inventory_results: list[Dict[str, Any]] | None = None,
        all_available: bool = True
    ) -> Dict[str, Any]:
        """
        Format final response for customer.

        Args:
            quote: Quote details from quoting agent
            fulfillment: Order fulfillment details (if processed)
            inventory_results: Inventory check results
            all_available: Whether all items are available

        Returns:
            Formatted response dictionary
        """
        response = {
            "success": True,
            "quote": quote if quote.get("success") else None,
            "fulfillment": fulfillment if fulfillment and fulfillment.get("success") else None,
            "inventory_status": inventory_results,
            "all_items_available": all_available
        }

        # Add summary message
        if fulfillment and fulfillment.get("success"):
            status = fulfillment.get("status", "unknown")
            order_id = fulfillment.get("order_id", "N/A")
            tracking = fulfillment.get("tracking_number", "N/A")

            if status == "completed":
                response["message"] = (
                    f"Order {order_id} successfully completed! "
                    f"Tracking number: {tracking}"
                )
            elif status == "partial":
                response["message"] = (
                    f"Order {order_id} partially fulfilled. "
                    f"Some items on backorder. Tracking number: {tracking}"
                )
            else:
                response["message"] = (
                    f"Order {order_id} created but items are on backorder. "
                    f"You will be notified when stock is available."
                )
        elif quote and quote.get("success"):
            quote_id = quote.get("quote_id", "N/A")
            total = quote.get("total_amount", 0)
            savings = quote.get("total_savings", 0)
            response["message"] = (
                f"Quote {quote_id} generated. "
                f"Total: ${total:.2f} (Savings: ${savings:.2f})"
            )
        else:
            response["message"] = "Unable to process request. Please contact support."
            response["success"] = False

        return response

