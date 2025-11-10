"""Fulfillment business logic service."""

from datetime import datetime, timedelta
from uuid import uuid4

from multi_agent_system.core.exceptions import RecordNotFoundError
from multi_agent_system.database.repositories.inventory import InventoryRepository
from multi_agent_system.database.repositories.transaction import TransactionRepository
from multi_agent_system.domain.enums import OrderStatus
from multi_agent_system.domain.models import (
    OrderResponse,
    QuoteItemRequest,
    QuoteItemResponse,
)


class FulfillmentService:
    """
    Service for order fulfillment and inventory allocation.

    Handles order processing, inventory allocation, backorder management,
    transaction recording, and reorder triggering.

    Example Usage:
    ```python
    fulfillment_service = FulfillmentService(inventory_repo, transaction_repo)

    # Process order
    items = [QuoteItemRequest(item_name="A4 paper", quantity=1000)]
    order = fulfillment_service.process_order(items, "CUST-001", datetime.now())
    ```
    """

    def __init__(
        self,
        inventory_repository: InventoryRepository,
        transaction_repository: TransactionRepository
    ):
        """
        Initialize fulfillment service.

        Args:
            inventory_repository: Repository for inventory data access
            transaction_repository: Repository for transaction data access
        """
        self.inventory_repo = inventory_repository
        self.transaction_repo = transaction_repository

    def process_order(
        self,
        items: list[QuoteItemRequest],
        customer_id: str,
        request_date: datetime,
        quote_id: str | None = None
    ) -> OrderResponse:
        """
        Process an order and allocate inventory.

        Args:
            items: List of items to order
            customer_id: Customer identifier
            request_date: Date of order request
            quote_id: Associated quote ID (optional)

        Returns:
            OrderResponse with fulfillment status

        Raises:
            RecordNotFoundError: If any item not found
        """
        # Generate unique order ID
        order_id = f"ORD-{uuid4().hex[:8].upper()}"

        # Allocate inventory for items
        allocation_result = self.allocate_inventory(items)

        items_fulfilled: list[QuoteItemResponse] = []
        backorder_items: list[QuoteItemRequest] = []
        total_amount = 0.0

        for item_request in items:
            inventory_item = self.inventory_repo.get_by_item_name(item_request.item_name)
            if not inventory_item:
                raise RecordNotFoundError(f"Item not found: {item_request.item_name}") # noqa: EM102

            allocated_qty = allocation_result.get(item_request.item_name, 0)

            if allocated_qty >= item_request.quantity:
                # Fully fulfilled
                subtotal = item_request.quantity * inventory_item.unit_price
                items_fulfilled.append(
                    QuoteItemResponse(
                        item_name=item_request.item_name,
                        quantity=item_request.quantity,
                        unit_price=inventory_item.unit_price,
                        discounted_price=inventory_item.unit_price,
                        discount_percent=0.0,
                        subtotal=subtotal
                    )
                )
                total_amount += subtotal

                # Record sale transaction
                self.record_sale_transaction(
                    item_request.item_name,
                    item_request.quantity,
                    subtotal,
                    request_date
                )
            elif allocated_qty > 0:
                # Partially fulfilled
                subtotal = allocated_qty * inventory_item.unit_price
                items_fulfilled.append(
                    QuoteItemResponse(
                        item_name=item_request.item_name,
                        quantity=allocated_qty,
                        unit_price=inventory_item.unit_price,
                        discounted_price=inventory_item.unit_price,
                        discount_percent=0.0,
                        subtotal=subtotal
                    )
                )
                total_amount += subtotal

                # Record sale transaction for fulfilled portion
                self.record_sale_transaction(
                    item_request.item_name,
                    allocated_qty,
                    subtotal,
                    request_date
                )

                # Create backorder for remaining
                backorder_qty = item_request.quantity - allocated_qty
                backorder_items.append(
                    QuoteItemRequest(
                        item_name=item_request.item_name,
                        quantity=backorder_qty
                    )
                )

                # Trigger reorder
                self.trigger_reorder(item_request.item_name, backorder_qty)
            else:
                # Not fulfilled at all
                backorder_items.append(item_request)
                self.trigger_reorder(item_request.item_name, item_request.quantity)

        # Determine order status
        if len(backorder_items) == 0:
            status = OrderStatus.COMPLETED
            delivery_date = request_date + timedelta(days=2)
        elif len(items_fulfilled) == 0:
            status = OrderStatus.PENDING
            delivery_date = request_date + timedelta(days=7)
        else:
            status = OrderStatus.PARTIAL
            delivery_date = request_date + timedelta(days=5)

        # Generate tracking number
        tracking_number = f"TRK-{uuid4().hex[:12].upper()}"

        return OrderResponse(
            order_id=order_id,
            customer_id=customer_id,
            quote_id=quote_id,
            status=status,
            items_fulfilled=items_fulfilled,
            backorder_items=backorder_items,
            total_amount=total_amount,
            delivery_date=delivery_date,
            tracking_number=tracking_number,
            created_at=request_date
        )

    def allocate_inventory(self, items: list[QuoteItemRequest]) -> dict[str, int]:
        """
        Allocate inventory for order items.

        Args:
            items: List of items to allocate

        Returns:
            Dictionary mapping item names to allocated quantities
        """
        allocation: dict[str, int] = {}

        for item in items:
            inventory_item = self.inventory_repo.get_by_item_name(item.item_name)
            if not inventory_item:
                allocation[item.item_name] = 0
                continue

            # Allocate what's available
            allocated = min(inventory_item.current_stock, item.quantity)
            allocation[item.item_name] = allocated

            # Update stock if allocated
            if allocated > 0:
                self.inventory_repo.update_stock(item.item_name, -allocated)

        return allocation

    def create_backorder(
        self,
        item_name: str,
        quantity: int,
        expected_date: datetime | None = None
    ) -> dict[str, str | int | datetime]:
        """
        Create a backorder for an item.

        Args:
            item_name: Name of the item
            quantity: Quantity on backorder
            expected_date: Expected fulfillment date

        Returns:
            Dictionary with backorder information
        """
        if expected_date is None:
            expected_date = datetime.now() + timedelta(days=7) # noqa: DTZ005

        return {
            "item_name": item_name,
            "quantity": quantity,
            "status": OrderStatus.PENDING.value,
            "expected_date": expected_date
        }

    def record_sale_transaction(
        self,
        item_name: str,
        quantity: int,
        price: float,
        transaction_date: datetime
    ) -> int:
        """
        Record a sale transaction.

        Args:
            item_name: Name of the item
            quantity: Quantity sold
            price: Total sale price
            transaction_date: Date of transaction

        Returns:
            Transaction ID
        """
        transaction = self.transaction_repo.create_sale(
            item_name=item_name,
            units=quantity,
            price=price,
            transaction_date=transaction_date
        )
        return transaction.id

    def trigger_reorder(self, item_name: str, quantity: int) -> None:
        """
        Trigger a reorder for an item.

        Creates a stock order transaction to track the reorder need.

        Args:
            item_name: Name of the item
            quantity: Quantity to reorder
        """
        # In a real system, this would trigger supplier integration
        # For now, we just record it as a pending stock order

        # Calculate cost (using unit price from inventory)
        inventory_item = self.inventory_repo.get_by_item_name(item_name)
        if not inventory_item:
            return

        # Assume supplier cost is 70% of unit price
        supplier_cost = inventory_item.unit_price * 0.7
        total_cost = supplier_cost * quantity

        # Record as stock order transaction
        self.transaction_repo.create_stock_order(
            item_name=item_name,
            units=quantity,
            price=total_cost,
            transaction_date=datetime.now() # noqa: DTZ005
        )

