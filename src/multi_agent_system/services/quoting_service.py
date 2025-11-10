"""Quoting business logic service."""

from datetime import datetime, timedelta
from uuid import uuid4

from multi_agent_system.core.exceptions import RecordNotFoundError
from multi_agent_system.database.models import QuoteItemModel, QuoteModel
from multi_agent_system.database.repositories.inventory import InventoryRepository
from multi_agent_system.database.repositories.quote import QuoteRepository
from multi_agent_system.domain.models import QuoteItemRequest, QuoteItemResponse, QuoteResponse


class QuotingService:
    """
    Service for quote generation and management.

    Handles quote creation, pricing with bulk discounts, quote searching,
    validation, and expiration management.

    Example Usage:
    ```python
    quoting_service = QuotingService(quote_repo, inventory_repo)

    # Generate quote
    items = [QuoteItemRequest(item_name="A4 paper", quantity=1000)]
    quote = quoting_service.generate_quote(items, "CUST-001", datetime.now())
    ```
    """

    def __init__(
        self,
        quote_repository: QuoteRepository,
        inventory_repository: InventoryRepository
    ):
        """
        Initialize quoting service.

        Args:
            quote_repository: Repository for quote data access
            inventory_repository: Repository for inventory data access
        """
        self.quote_repo = quote_repository
        self.inventory_repo = inventory_repository

    def generate_quote(
        self,
        items: list[QuoteItemRequest],
        customer_id: str,
        request_date: datetime,
        notes: str | None = None
    ) -> QuoteResponse:
        """
        Generate a new quote for customer.

        Args:
            items: List of requested items
            customer_id: Customer identifier
            request_date: Date of quote request
            notes: Additional notes for the quote

        Returns:
            QuoteResponse with pricing and delivery details

        Raises:
            RecordNotFoundError: If any item not found
        """
        # Generate unique quote ID
        quote_id = f"Q-{datetime.now().year}-{uuid4().hex[:6].upper()}" # noqa: DTZ005

        # Calculate pricing for each item
        quote_items: list[QuoteItemResponse] = []
        total_amount = 0.0
        total_savings = 0.0

        for item_request in items:
            inventory_item = self.inventory_repo.get_by_item_name(item_request.item_name)
            if not inventory_item:
                raise RecordNotFoundError(f"Item not found: {item_request.item_name}") # noqa: EM102

            unit_price = inventory_item.unit_price
            discounted_price, discount_percent = self.calculate_bulk_discount(
                item_request.quantity,
                unit_price
            )
            subtotal = item_request.quantity * discounted_price
            savings = item_request.quantity * (unit_price - discounted_price)

            quote_items.append(
                QuoteItemResponse(
                    item_name=item_request.item_name,
                    quantity=item_request.quantity,
                    unit_price=unit_price,
                    discounted_price=discounted_price,
                    discount_percent=discount_percent,
                    subtotal=subtotal
                )
            )

            total_amount += subtotal
            total_savings += savings

        # Calculate delivery date (5 business days from request)
        delivery_date = request_date + timedelta(days=5)

        # Quote valid for 30 days
        valid_until = request_date + timedelta(days=30)

        # Create quote response
        quote_response = QuoteResponse(
            quote_id=quote_id,
            customer_id=customer_id,
            items=quote_items,
            total_amount=total_amount,
            total_savings=total_savings,
            delivery_date=delivery_date,
            valid_until=valid_until,
            status="pending",
            created_at=request_date,
            quote_explanation=notes
        )

        # Save to database
        quote_model = QuoteModel(
            quote_id=quote_id,
            customer_id=customer_id,
            total_amount=total_amount,
            delivery_date=delivery_date,
            valid_until=valid_until,
            status="pending",
            created_at=request_date,
            quote_explanation=notes
        )
        created_quote = self.quote_repo.create(quote_model)

        # Save quote items
        for item in quote_items:
            quote_item_model = QuoteItemModel(
                quote_id=created_quote.id,
                item_name=item.item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discounted_price=item.discounted_price,
                discount_percent=item.discount_percent,
                subtotal=item.subtotal
            )
            self.quote_repo.session.add(quote_item_model)

        self.quote_repo.session.flush()

        return quote_response

    def search_historical_quotes(self, search_terms: list[str]) -> list[QuoteModel]:
        """
        Search for quotes by search terms.

        Searches in quote_id, customer_id, and quote_explanation fields.

        Args:
            search_terms: List of search terms

        Returns:
            List of matching quotes
        """
        return self.quote_repo.search_quotes(search_terms)

    def calculate_bulk_discount(
        self,
        quantity: int,
        unit_price: float
    ) -> tuple[float, float]:
        """
        Calculate bulk discount based on quantity.

        Discount tiers:
        - 1000+ units: 5% discount
        - 5000+ units: 10% discount
        - 10000+ units: 15% discount

        Args:
            quantity: Order quantity
            unit_price: Regular unit price

        Returns:
            Tuple of (discounted_price, discount_percent)
        """
        if quantity >= 10000:
            discount_percent = 0.15
        elif quantity >= 5000:
            discount_percent = 0.10
        elif quantity >= 1000:
            discount_percent = 0.05
        else:
            discount_percent = 0.0

        discounted_price = unit_price * (1 - discount_percent)
        return discounted_price, discount_percent

    def validate_quote(self, quote_id: str) -> bool:
        """
        Validate if a quote exists and is still valid.

        Args:
            quote_id: Unique quote identifier

        Returns:
            True if quote exists and is not expired, False otherwise
        """
        quote = self.quote_repo.get_by_quote_id(quote_id)
        if not quote:
            return False

        # Check if expired
        return datetime.now() <= quote.valid_until # noqa: DTZ005

    def expire_old_quotes(self) -> int:
        """
        Mark expired quotes as expired.

        Returns:
            Number of quotes expired
        """
        expired_quotes = self.quote_repo.get_expired_quotes()
        count = 0

        for quote in expired_quotes:
            if quote.status == "pending":
                quote.status = "expired"
                self.quote_repo.session.flush()
                count += 1

        return count

