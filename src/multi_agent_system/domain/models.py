"""
Domain models using Pydantic.

These models represent the core business entities and are used for
validation, serialization, and API request/response schemas.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from multi_agent_system.domain.enums import ItemCategory, OrderStatus, TransactionType

# 3. Add custom validators where needed
# 4. Use proper types (datetime, UUID, etc.)
# 5. Provide examples in docstrings
# 6. Separate request/response models from internal models

# Example Implementation:


class ItemBase(BaseModel):
    """
    Base model for inventory items.

    Attributes:
        item_name: Name of the item
        category: Item category
        unit_price: Price per unit
    """

    item_name: str = Field(..., description="Name of the item", min_length=1)
    category: ItemCategory = Field(..., description="Item category")
    unit_price: float = Field(..., description="Price per unit", gt=0)


class InventoryItem(ItemBase):
    """
    Inventory item with stock information.

    Attributes:
        current_stock: Current stock quantity
        min_stock_level: Minimum stock level before reorder
    """

    current_stock: int = Field(..., description="Current stock quantity", ge=0)
    min_stock_level: int = Field(..., description="Minimum stock level", ge=0)


class QuoteItemRequest(BaseModel):
    """
    Single item in a quote request.

    Example:
        >>> item = QuoteItemRequest(item_name="A4 paper", quantity=1000)
        >>> print(item.model_dump())
        {'item_name': 'A4 paper', 'quantity': 1000}
    """

    item_name: str = Field(..., description="Name of the item")
    quantity: int = Field(..., description="Requested quantity", gt=0)


class QuoteRequest(BaseModel):
    """
    Request for a quote from a customer.

    TODO: Complete implementation

    Expected Input:
    ```json
    {
        "customer_id": "CUST-001",
        "items": [
            {"item_name": "A4 paper", "quantity": 1000},
            {"item_name": "Glossy paper", "quantity": 500}
        ],
        "request_date": "2025-01-10T10:00:00Z",
        "notes": "Urgent order for corporate event"
    }
    ```

    Expected Output: Validated QuoteRequest object
    """

    customer_id: str = Field(..., description="Customer identifier")
    items: list[QuoteItemRequest] = Field(..., description="Requested items", min_length=1)
    request_date: datetime = Field(
        default_factory=datetime.now,
        description="Date of request"
    )
    notes: str | None = Field(None, description="Additional notes")

    @property
    def total_items(self) -> int:
        """Calculate total number of item types."""
        return len(self.items)

    @property
    def total_quantity(self) -> int:
        """Calculate total quantity across all items."""
        return sum(item.quantity for item in self.items)


class QuoteItemResponse(BaseModel):
    """
    Single item in a quote response with pricing.

    Attributes:
        item_name: Name of the item
        quantity: Requested quantity
        unit_price: Regular unit price
        discounted_price: Price per unit after discount
        discount_percent: Discount percentage applied (0-1)
        subtotal: Total price for this item (quantity * discounted_price)
    """

    item_name: str = Field(..., description="Name of the item")
    quantity: int = Field(..., description="Requested quantity", gt=0)
    unit_price: float = Field(..., description="Regular unit price", gt=0)
    discounted_price: float = Field(..., description="Price after discount", gt=0)
    discount_percent: float = Field(..., description="Discount percentage", ge=0, le=1)
    subtotal: float = Field(..., description="Total price for this item", ge=0)

    @field_validator("discounted_price")
    @classmethod
    def validate_discounted_price(cls, v: float, info: Any) -> float:
        """Ensure discounted price is not greater than unit price."""
        if "unit_price" in info.data and v > info.data["unit_price"]:
            msg = "Discounted price cannot be greater than unit price"
            raise ValueError(msg)
        return v


class QuoteResponse(BaseModel):
    """
    Quote response with pricing and delivery information.

    Example Output:
    ```json
    {
        "quote_id": "Q-2025-001",
        "customer_id": "CUST-001",
        "items": [
            {
                "item_name": "A4 paper",
                "quantity": 1000,
                "unit_price": 0.05,
                "discounted_price": 0.0475,
                "discount_percent": 0.05,
                "subtotal": 47.50
            }
        ],
        "total_amount": 142.50,
        "total_savings": 7.50,
        "delivery_date": "2025-01-15",
        "valid_until": "2025-02-09",
        "status": "pending",
        "created_at": "2025-01-10T10:00:00Z"
    }
    ```
    """

    quote_id: str = Field(..., description="Unique quote identifier")
    customer_id: str = Field(..., description="Customer identifier")
    items: list[QuoteItemResponse] = Field(..., description="Quote items with pricing", min_length=1)
    total_amount: float = Field(..., description="Total amount after discounts", ge=0)
    total_savings: float = Field(..., description="Total savings from discounts", ge=0)
    delivery_date: datetime = Field(..., description="Expected delivery date")
    valid_until: datetime = Field(..., description="Quote expiration date")
    status: str = Field(default="pending", description="Quote status")
    created_at: datetime = Field(default_factory=datetime.now, description="Quote creation date")
    quote_explanation: str | None = Field(None, description="Additional quote explanation")

    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        return datetime.now() > self.valid_until

    @property
    def total_items(self) -> int:
        """Calculate total number of item types."""
        return len(self.items)

    @property
    def total_quantity(self) -> int:
        """Calculate total quantity across all items."""
        return sum(item.quantity for item in self.items)


class OrderRequest(BaseModel):
    """
    Request to fulfill an order based on a quote.

    Attributes:
        order_id: Unique order identifier
        quote_id: Associated quote identifier
        customer_id: Customer identifier
        items: List of items to order
        request_date: Order request date
    """

    order_id: str = Field(default_factory=lambda: f"ORD-{uuid4().hex[:8].upper()}", description="Unique order identifier")
    quote_id: str = Field(..., description="Associated quote identifier")
    customer_id: str = Field(..., description="Customer identifier")
    items: list[QuoteItemRequest] = Field(..., description="Items to order", min_length=1)
    request_date: datetime = Field(default_factory=datetime.now, description="Order request date")


class OrderResponse(BaseModel):
    """
    Response for order fulfillment.

    Attributes:
        order_id: Unique order identifier
        status: Current order status
        items_fulfilled: List of items successfully fulfilled
        backorder_items: List of items on backorder
        total_amount: Total order amount
        delivery_date: Expected delivery date
        tracking_number: Shipment tracking number (if available)
        created_at: Order creation timestamp
    """

    order_id: str = Field(..., description="Unique order identifier")
    status: OrderStatus = Field(..., description="Current order status")
    items_fulfilled: list[QuoteItemResponse] = Field(default_factory=list, description="Items successfully fulfilled")
    backorder_items: list[QuoteItemRequest] = Field(default_factory=list, description="Items on backorder")
    total_amount: float = Field(..., description="Total order amount", ge=0)
    delivery_date: datetime = Field(..., description="Expected delivery date")
    tracking_number: str | None = Field(None, description="Shipment tracking number")
    created_at: datetime = Field(default_factory=datetime.now, description="Order creation timestamp")

    @property
    def has_backorders(self) -> bool:
        """Check if order has any backorder items."""
        return len(self.backorder_items) > 0

    @property
    def is_fully_fulfilled(self) -> bool:
        """Check if all items are fulfilled."""
        return len(self.backorder_items) == 0


class InventoryCheckResult(BaseModel):
    """
    Result of inventory availability check.

    Attributes:
        item_name: Name of the item
        requested_quantity: Quantity requested
        current_stock: Current stock level
        available: Whether sufficient stock is available
        shortage: Quantity short (0 if available)
        needs_reorder: Whether reorder is needed
        reorder_quantity: Quantity to reorder (if applicable)
        supplier_eta: Expected arrival from supplier
    """

    item_name: str = Field(..., description="Name of the item")
    requested_quantity: int = Field(..., description="Quantity requested", ge=0)
    current_stock: int = Field(..., description="Current stock level", ge=0)
    available: bool = Field(..., description="Whether sufficient stock is available")
    shortage: int = Field(default=0, description="Quantity short", ge=0)
    needs_reorder: bool = Field(default=False, description="Whether reorder is needed")
    reorder_quantity: int | None = Field(None, description="Quantity to reorder", ge=0)
    supplier_eta: datetime | None = Field(None, description="Expected arrival from supplier")

    @property
    def fulfillment_percentage(self) -> float:
        """Calculate what percentage can be fulfilled."""
        if self.requested_quantity == 0:
            return 0.0
        return min(self.current_stock / self.requested_quantity, 1.0) * 100


class Transaction(BaseModel):
    """
    Financial transaction record.

    Attributes:
        id: Transaction identifier (auto-generated)
        item_name: Name of item (None for cash transactions)
        transaction_type: Type of transaction
        units: Number of units (None for cash transactions)
        price: Transaction amount
        transaction_date: Date of transaction
    """

    id: int | None = Field(None, description="Transaction identifier")
    item_name: str | None = Field(None, description="Name of item (None for cash transactions)")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    units: int | None = Field(None, description="Number of units (None for cash transactions)", ge=0)
    price: float = Field(..., description="Transaction amount")
    transaction_date: datetime = Field(default_factory=datetime.now, description="Date of transaction")

    @field_validator("units")
    @classmethod
    def validate_units(cls, v: int | None, info: Any) -> int | None:
        """Validate that units is provided for non-cash transactions."""
        trans_type = info.data.get("transaction_type")
        if trans_type and trans_type != TransactionType.CASH_TRANSACTION and v is None:
            msg = "Units must be provided for non-cash transactions"
            raise ValueError(msg)
        return v

    @field_validator("item_name")
    @classmethod
    def validate_item_name(cls, v: str | None, info: Any) -> str | None:
        """Validate that item_name is provided for non-cash transactions."""
        trans_type = info.data.get("transaction_type")
        if trans_type and trans_type != TransactionType.CASH_TRANSACTION and not v:
            msg = "Item name must be provided for non-cash transactions"
            raise ValueError(msg)
        return v


class FinancialReport(BaseModel):
    """
    Comprehensive financial report.

    Attributes:
        as_of_date: Report generation date
        cash_balance: Current cash balance
        inventory_value: Total value of inventory
        total_assets: Total assets (cash + inventory)
        inventory_summary: Summary of inventory items
        top_selling_products: List of top selling products
        total_revenue: Total revenue
        total_expenses: Total expenses
        net_profit: Net profit (revenue - expenses)
    """

    as_of_date: datetime = Field(default_factory=datetime.now, description="Report generation date")
    cash_balance: float = Field(..., description="Current cash balance")
    inventory_value: float = Field(..., description="Total value of inventory", ge=0)
    total_assets: float = Field(..., description="Total assets (cash + inventory)")
    inventory_summary: list[dict[str, Any]] = Field(default_factory=list, description="Summary of inventory items")
    top_selling_products: list[dict[str, Any]] = Field(default_factory=list, description="Top selling products")
    total_revenue: float = Field(default=0.0, description="Total revenue", ge=0)
    total_expenses: float = Field(default=0.0, description="Total expenses", ge=0)
    net_profit: float = Field(default=0.0, description="Net profit (revenue - expenses)")

    @property
    def profit_margin(self) -> float:
        """Calculate profit margin as percentage."""
        if self.total_revenue == 0:
            return 0.0
        return (self.net_profit / self.total_revenue) * 100

    @property
    def expense_ratio(self) -> float:
        """Calculate expense ratio as percentage."""
        if self.total_revenue == 0:
            return 0.0
        return (self.total_expenses / self.total_revenue) * 100

