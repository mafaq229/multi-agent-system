"""Inventory business logic service."""

from datetime import datetime, timedelta

from multi_agent_system.core.exceptions import RecordNotFoundError
from multi_agent_system.database.repositories.inventory import InventoryRepository
from multi_agent_system.domain.enums import ItemCategory
from multi_agent_system.domain.models import InventoryCheckResult, InventoryItem


class InventoryService:
    """
    Service for inventory business logic.

    Handles inventory availability checks, stock management, reorder calculations,
    and supplier delivery estimates.

    Example Usage:
    ```python
    inventory_service = InventoryService(inventory_repo)

    # Check availability
    result = inventory_service.check_availability("A4 paper", 1000, datetime.now())

    # Get low stock items
    low_stock = inventory_service.get_low_stock_items()
    ```
    """

    def __init__(self, inventory_repository: InventoryRepository):
        """
        Initialize inventory service.

        Args:
            inventory_repository: Repository for inventory data access
        """
        self.repository = inventory_repository

    def check_availability(
        self,
        item_name: str,
        quantity: int,
        as_of_date: datetime
    ) -> InventoryCheckResult:
        """
        Check if item is available in requested quantity.

        Args:
            item_name: Name of the item
            quantity: Requested quantity
            as_of_date: Date for availability check

        Returns:
            InventoryCheckResult with availability details

        Raises:
            RecordNotFoundError: If item not found
        """
        item = self.repository.get_by_item_name(item_name)
        if not item:
            error_msg = f"Item not found: {item_name}"
            raise RecordNotFoundError(error_msg)

        available = item.current_stock >= quantity
        shortage = max(0, quantity - item.current_stock)
        needs_reorder = item.current_stock <= item.min_stock_level

        reorder_quantity = None
        supplier_eta = None
        if needs_reorder:
            reorder_quantity = self.calculate_reorder_quantity(item_name)
            supplier_eta = self.get_supplier_delivery_date(reorder_quantity, as_of_date)

        return InventoryCheckResult(
            item_name=item_name,
            requested_quantity=quantity,
            current_stock=item.current_stock,
            available=available,
            shortage=shortage,
            needs_reorder=needs_reorder,
            reorder_quantity=reorder_quantity,
            supplier_eta=supplier_eta
        )

    def get_all_inventory(self, as_of_date: datetime) -> dict[str, int]:  # noqa: ARG002
        """
        Get current stock levels for all items.

        Args:
            as_of_date: Date for inventory snapshot (reserved for future use)

        Returns:
            Dictionary mapping item names to stock levels
        """
        items = self.repository.get_all(limit=10000)
        return {item.item_name: item.current_stock for item in items}

    def get_low_stock_items(self) -> list[InventoryItem]:
        """
        Get items that are at or below minimum stock level.

        Returns:
            List of InventoryItem objects for low stock items
        """
        items = self.repository.get_low_stock_items()
        return [
            InventoryItem(
                item_name=item.item_name,
                category=ItemCategory(item.category),
                unit_price=item.unit_price,
                current_stock=item.current_stock,
                min_stock_level=item.min_stock_level
            )
            for item in items
        ]

    def calculate_reorder_quantity(self, item_name: str) -> int:
        """
        Calculate recommended reorder quantity for an item.

        Uses formula: max(shortage, min_stock_level * 2) to ensure adequate buffer.

        Args:
            item_name: Name of the item

        Returns:
            Recommended reorder quantity

        Raises:
            RecordNotFoundError: If item not found
        """
        item = self.repository.get_by_item_name(item_name)
        if not item:
            error_msg = f"Item not found: {item_name}"
            raise RecordNotFoundError(error_msg)

        # Reorder enough to reach 2x minimum stock level
        shortage = max(0, item.min_stock_level - item.current_stock)
        return max(shortage, item.min_stock_level * 2)

    def get_supplier_delivery_date(self, quantity: int, request_date: datetime) -> datetime:
        """
        Estimate supplier delivery date based on order quantity.

        Delivery time calculation:
        - Small orders (< 1000 units): 3 business days
        - Medium orders (1000-5000 units): 5 business days
        - Large orders (> 5000 units): 7 business days

        Args:
            quantity: Order quantity
            request_date: Date of request

        Returns:
            Estimated delivery date
        """
        if quantity < 1000:
            days = 3
        elif quantity < 5000:
            days = 5
        else:
            days = 7

        return request_date + timedelta(days=days)

    def update_stock_level(self, item_name: str, quantity_delta: int) -> None:
        """
        Update stock level for an item.

        Args:
            item_name: Name of the item
            quantity_delta: Change in quantity (positive to add, negative to subtract)

        Raises:
            RecordNotFoundError: If item not found
        """
        item = self.repository.update_stock(item_name, quantity_delta)
        if not item:
            error_msg = f"Item not found: {item_name}"
            raise RecordNotFoundError(error_msg)

    def get_inventory_value(self) -> float:
        """
        Calculate total value of all inventory.

        Returns:
            Total inventory value (sum of current_stock * unit_price for all items)
        """
        return self.repository.get_inventory_value()

