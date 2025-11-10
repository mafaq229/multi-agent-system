"""
Inventory repository with specialized queries.

This repository extends the base repository with inventory-specific
operations like stock checks, low stock alerts, etc.
"""

from sqlalchemy.orm import Session

from multi_agent_system.database.models import InventoryModel
from multi_agent_system.database.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryModel]):
    """
    Repository for inventory operations.

    Extends BaseRepository with inventory-specific methods for stock
    management, low stock alerts, category filtering, and price queries.
    """

    def __init__(self, session: Session):
        """Initialize repository with session."""
        super().__init__(InventoryModel, session)

    def get_by_item_name(self, item_name: str) -> InventoryModel | None:
        """Get inventory by item name."""
        return self.session.query(self.model).filter(
            self.model.item_name == item_name
        ).first()

    def get_low_stock_items(self) -> list[InventoryModel]:
        """Get items below minimum stock level."""
        return self.session.query(self.model).filter(
            self.model.current_stock <= self.model.min_stock_level
        ).all()

    def get_by_category(self, category: str) -> list[InventoryModel]:
        """Get all items in a category."""
        return self.session.query(self.model).filter(
            self.model.category == category
        ).all()

    def update_stock(self, item_name: str, quantity_delta: int) -> InventoryModel | None:
        """
        Update stock quantity (positive or negative delta).

        Args:
            item_name: Name of the item
            quantity_delta: Change in quantity (positive to add, negative to subtract)

        Returns:
            Updated inventory model or None if item not found
        """
        item = self.get_by_item_name(item_name)
        if item:
            item.current_stock += quantity_delta
            self.session.flush()
            self.session.refresh(item)
        return item

    def get_inventory_value(self) -> float:
        """Calculate total inventory value."""
        items = self.get_all()
        return sum(item.current_stock * item.unit_price for item in items)

    def search_items(self, query: str) -> list[InventoryModel]:
        """
        Search items by name (case-insensitive partial match).

        Args:
            query: Search term

        Returns:
            List of matching inventory items
        """
        return self.session.query(self.model).filter(
            self.model.item_name.ilike(f"%{query}%")
        ).all()

    def get_price_range(
        self,
        min_price: float,
        max_price: float
    ) -> list[InventoryModel]:
        """
        Get items within a price range.

        Args:
            min_price: Minimum unit price
            max_price: Maximum unit price

        Returns:
            List of items within the price range
        """
        return self.session.query(self.model).filter(
            self.model.unit_price >= min_price,
            self.model.unit_price <= max_price
        ).all()

