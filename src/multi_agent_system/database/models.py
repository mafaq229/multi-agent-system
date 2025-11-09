"""
SQLAlchemy ORM models for database tables.

These models map to database tables and define relationships,
constraints, and indexes.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class InventoryModel(Base):
    """
    Inventory table model.

    Maps to the 'inventory' table containing product information
    and stock levels.
    """

    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    min_stock_level: Mapped[int] = mapped_column(Integer, default=50)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<InventoryModel(id={self.id}, item_name='{self.item_name}', stock={self.current_stock})>"


class TransactionModel(Base):
    """
    Transaction table model.

    Maps to the 'transactions' table containing all financial transactions
    (sales and stock orders).
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_name: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("inventory.item_name"),
        nullable=True,  # nullable for cash transactions
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        doc="Type of transaction: 'sales' or 'stock_orders'",
    )
    units: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="Quantity of items; nullable for cash transactions")
    price: Mapped[float] = mapped_column(Float, nullable=False, doc="Transaction amount")
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    inventory: Mapped["InventoryModel"] = relationship(
        "InventoryModel",
        primaryjoin="TransactionModel.item_name == InventoryModel.item_name",
        backref="transactions",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<TransactionModel(id={self.id}, item_name={self.item_name!r}, "
            f"type={self.transaction_type!r}, units={self.units}, price={self.price}, "
            f"transaction_date={self.transaction_date})>"
        )


class QuoteRequestModel(Base):
    """
    Quote request table model.

    Maps to the 'quote_requests' table containing customer inquiries.
    """

    __tablename__ = "quote_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    request_text: Mapped[str] = mapped_column(Text, nullable=False)
    request_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    quote: Mapped[Optional["QuoteModel"]] = relationship(
        "QuoteModel",
        back_populates="request",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            f"<QuoteRequestModel(id={self.id}, customer_id='{self.customer_id}', "
            f"status='{self.status}', request_date={self.request_date})>"
        )


class QuoteModel(Base):
    """
    Quote table model.

    Maps to the 'quotes' table containing generated quotes.
    """

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quote_requests.id"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_discount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quote_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    request: Mapped["QuoteRequestModel"] = relationship(
        "QuoteRequestModel",
        back_populates="quote",
    )
    items: Mapped[list["QuoteItemModel"]] = relationship(
        "QuoteItemModel",
        back_populates="quote",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<QuoteModel(id={self.id}, quote_id='{self.quote_id}', "
            f"customer_id='{self.customer_id}', total_amount={self.total_amount}, "
            f"status='{self.status}')>"
        )


class QuoteItemModel(Base):
    """
    Quote item table model.

    Maps to the 'quote_items' table containing individual items in quotes.
    """

    __tablename__ = "quote_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quotes.id"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discounted_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    quote: Mapped["QuoteModel"] = relationship(
        "QuoteModel",
        back_populates="items",
    )

    def __repr__(self) -> str:
        return (
            f"<QuoteItemModel(id={self.id}, quote_id={self.quote_id}, "
            f"item_name='{self.item_name}', quantity={self.quantity}, "
            f"subtotal={self.subtotal})>"
        )


# TODO: Add more models as needed
# Examples:
# - OrderModel: Order tracking
# - OrderItemModel: Items in orders
# - CustomerModel: Customer information
# - SupplierModel: Supplier information
# - AuditLogModel: Audit trail for changes


# TODO: Add indexes for performance
# Example:
# Index('ix_transactions_date', TransactionModel.transaction_date)
# Index('ix_quotes_status_date', QuoteModel.status, QuoteModel.created_at)

