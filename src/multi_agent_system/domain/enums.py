"""
Enumerations for domain concepts.

This module defines all enum types used across the application for
type safety and validation.
"""

from enum import Enum


# TODO: change these as per the project requirements later on
class TransactionType(str, Enum):
    """
    Types of transactions in the system.

    Attributes:
        SALE: Revenue from customer orders
        STOCK_ORDER: Purchase from suppliers
        CASH_TRANSACTION: Direct cash transaction (no inventory)
    """

    SALE = "sales"
    STOCK_ORDER = "stock_orders"
    CASH_TRANSACTION = "cash_transaction"


class OrderStatus(str, Enum):
    """
    Status of an order.

    Attributes:
        PENDING: Order received but not processed
        FULFILLED: Order completely fulfilled
        PARTIAL: Order partially fulfilled with backorders
        BACKORDERED: Order waiting for inventory
        CANCELLED: Order cancelled
        COMPLETED: Order delivered and closed
    """

    PENDING = "pending"
    FULFILLED = "fulfilled"
    PARTIAL = "partial"
    BACKORDERED = "backordered"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ItemCategory(str, Enum):
    """
    Categories of inventory items.

    Attributes:
        PAPER: Standard paper products
        PRODUCT: Finished products (plates, cups, etc.)
        LARGE_FORMAT: Large format printing materials
        SPECIALTY: Specialty paper products
    """

    PAPER = "paper"
    PRODUCT = "product"
    LARGE_FORMAT = "large_format"
    SPECIALTY = "specialty"

class AgentType(str, Enum):
    """
    Types of agents in the system.

    Attributes:
        ORCHESTRATOR: Central coordination agent
        INVENTORY: Handles inventory management and updates
        QUOTING: Handles generating and managing price quotes
        FULFILLMENT: Handles order fulfillment and processing
    """

    ORCHESTRATOR = "orchestrator"
    INVENTORY = "inventory"
    QUOTING = "quoting"
    FULFILLMENT = "fulfillment"

# TODO: Add more enums as needed
# Examples:
# - AgentType (ORCHESTRATOR, INVENTORY, QUOTING, FULFILLMENT)
# - QuoteStatus (DRAFT, PENDING, ACCEPTED, REJECTED, EXPIRED)
# - PaymentStatus (UNPAID, PAID, REFUNDED)
# - DeliveryStatus (PREPARING, SHIPPED, IN_TRANSIT, DELIVERED)
# - InventoryActionType (REORDER, ADJUST, TRANSFER)

