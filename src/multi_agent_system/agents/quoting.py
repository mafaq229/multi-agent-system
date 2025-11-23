"""Quoting Agent - Generate quotes with pricing and discounts."""

from datetime import datetime
from typing import Any, Dict

from multi_agent_system.agents.base import BaseAgent
from multi_agent_system.agents.prompts.quoting_prompts import QUOTING_SYSTEM_PROMPT
from multi_agent_system.domain.models import QuoteItemRequest
from multi_agent_system.services.quoting_service import QuotingService


class QuotingAgent(BaseAgent):
    """
    Quoting Agent for generating price quotes.

    Responsibilities:
    - Generate competitive quotes
    - Apply bulk discounts
    - Search historical quotes
    - Calculate delivery dates
    """

    def __init__(
        self,
        quoting_service: QuotingService,
        model: str = "openai:gpt-4o-mini",
        **kwargs
    ):
        """
        Initialize quoting agent.

        Args:
            quoting_service: Service for quoting operations
            model: Model identifier for the AI agent
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="quoting",
            model=model,
            system_prompt=QUOTING_SYSTEM_PROMPT,
            **kwargs
        )
        self.quoting_service = quoting_service
        self._register_tools()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process quote generation request.

        Args:
            input_data: Dictionary with:
                - items: List of items with quantities
                - customer_id: Customer identifier
                - request_date: Date of request
                - notes: Optional notes

        Returns:
            Dictionary with quote details
        """
        self._log_start(input_data)
        try:
            items = input_data["items"]
            customer_id = input_data.get("customer_id", "UNKNOWN")
            request_date = input_data.get("request_date", datetime.now())  # noqa: DTZ005
            notes = input_data.get("notes")

            if isinstance(request_date, str):
                request_date = datetime.fromisoformat(request_date)

            # Convert items to QuoteItemRequest objects
            quote_items = []
            for item in items:
                if isinstance(item, dict):
                    quote_items.append(
                        QuoteItemRequest(
                            item_name=item["item_name"],
                            quantity=item["quantity"]
                        )
                    )
                else:
                    quote_items.append(item)

            quote = self.quoting_service.generate_quote(
                items=quote_items,
                customer_id=customer_id,
                request_date=request_date,
                notes=notes
            )

            response = {
                "quote_id": quote.quote_id,
                "customer_id": quote.customer_id,
                "items": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "discounted_price": item.discounted_price,
                        "discount_percent": item.discount_percent,
                        "subtotal": item.subtotal
                    }
                    for item in quote.items
                ],
                "total_amount": quote.total_amount,
                "total_savings": quote.total_savings,
                "delivery_date": quote.delivery_date.isoformat(),
                "valid_until": quote.valid_until.isoformat(),
                "status": quote.status,
                "quote_explanation": quote.quote_explanation,
                "success": True
            }

            self._log_complete(response)
            return response

        except Exception as e:
            return self._handle_error(e)

    def _register_tools(self) -> None:
        """Register agent tools for quoting operations."""

        @self._agent.tool
        def generate_quote(
            items: list[Dict[str, Any]],
            customer_id: str,
            request_date: str | None = None,
            notes: str | None = None
        ) -> Dict[str, Any]:
            """
            Generate a new quote for customer.

            Args:
                items: List of dictionaries with item_name and quantity
                customer_id: Customer identifier
                request_date: Optional date of request (ISO format)
                notes: Optional notes for the quote

            Returns:
                Dictionary with quote details
            """
            date = datetime.fromisoformat(request_date) if request_date else datetime.now()  # noqa: DTZ005

            quote_items = [
                QuoteItemRequest(item_name=item["item_name"], quantity=item["quantity"])
                for item in items
            ]

            quote = self.quoting_service.generate_quote(
                items=quote_items,
                customer_id=customer_id,
                request_date=date,
                notes=notes
            )

            return {
                "quote_id": quote.quote_id,
                "customer_id": quote.customer_id,
                "items": [
                    {
                        "item_name": item.item_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "discounted_price": item.discounted_price,
                        "discount_percent": item.discount_percent,
                        "subtotal": item.subtotal
                    }
                    for item in quote.items
                ],
                "total_amount": quote.total_amount,
                "total_savings": quote.total_savings,
                "delivery_date": quote.delivery_date.isoformat(),
                "valid_until": quote.valid_until.isoformat(),
                "status": quote.status
            }

        @self._agent.tool
        def search_quotes(search_terms: list[str]) -> list[Dict[str, Any]]:
            """
            Search historical quotes by search terms.

            Args:
                search_terms: List of terms to search for

            Returns:
                List of matching quotes
            """
            quotes = self.quoting_service.search_historical_quotes(search_terms)
            return [
                {
                    "quote_id": quote.quote_id,
                    "customer_id": quote.customer_id,
                    "total_amount": quote.total_amount,
                    "status": quote.status,
                    "created_at": quote.created_at.isoformat(),
                    "valid_until": quote.valid_until.isoformat()
                }
                for quote in quotes
            ]

        @self._agent.tool
        def calculate_discount(quantity: int, unit_price: float) -> Dict[str, float]:
            """
            Calculate bulk discount for given quantity and price.

            Args:
                quantity: Order quantity
                unit_price: Regular unit price

            Returns:
                Dictionary with discounted_price and discount_percent
            """
            discounted_price, discount_percent = self.quoting_service.calculate_bulk_discount(
                quantity=quantity,
                unit_price=unit_price
            )
            return {
                "discounted_price": discounted_price,
                "discount_percent": discount_percent,
                "savings_per_unit": unit_price - discounted_price,
                "total_savings": (unit_price - discounted_price) * quantity
            }

        @self._agent.tool
        def validate_quote(quote_id: str) -> bool:
            """
            Validate if a quote exists and is still valid.

            Args:
                quote_id: Unique quote identifier

            Returns:
                True if quote is valid, False otherwise
            """
            return self.quoting_service.validate_quote(quote_id)

