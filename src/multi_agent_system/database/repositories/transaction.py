"""Transaction repository with financial queries."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from multi_agent_system.database.models import TransactionModel
from multi_agent_system.database.repositories.base import BaseRepository
from multi_agent_system.domain.enums import TransactionType


class TransactionRepository(BaseRepository[TransactionModel]):
    """
    Repository for transaction operations.

    Extends BaseRepository with transaction-specific methods for managing
    sales, stock orders, financial calculations, and reporting.
    """

    def __init__(self, session: Session):
        """Initialize repository with session."""
        super().__init__(TransactionModel, session)

    def create_sale(
        self,
        item_name: str,
        units: int,
        price: float,
        transaction_date: datetime | None = None
    ) -> TransactionModel:
        """
        Create a sale transaction.

        Args:
            item_name: Name of the item sold
            units: Number of units sold
            price: Total sale price
            transaction_date: Date of transaction (default: current date)

        Returns:
            Created transaction model
        """
        if transaction_date is None:
            transaction_date = datetime.now()  # noqa: DTZ005

        transaction = TransactionModel(
            item_name=item_name,
            transaction_type=TransactionType.SALE.value,
            units=units,
            price=price,
            transaction_date=transaction_date
        )
        return self.create(transaction)

    def create_stock_order(
        self,
        item_name: str,
        units: int,
        price: float,
        transaction_date: datetime | None = None
    ) -> TransactionModel:
        """
        Create a stock order transaction.

        Args:
            item_name: Name of the item ordered
            units: Number of units ordered
            price: Total order price
            transaction_date: Date of transaction (default: current date)

        Returns:
            Created transaction model
        """
        if transaction_date is None:
            transaction_date = datetime.now()  # noqa: DTZ005

        transaction = TransactionModel(
            item_name=item_name,
            transaction_type=TransactionType.STOCK_ORDER.value,
            units=units,
            price=price,
            transaction_date=transaction_date
        )
        return self.create(transaction)

    def create_cash_transaction(
        self,
        price: float,
        transaction_date: datetime | None = None
    ) -> TransactionModel:
        """
        Create a cash transaction (no inventory item).

        Args:
            price: Transaction amount (positive for income, negative for expense)
            transaction_date: Date of transaction (default: current date)

        Returns:
            Created transaction model
        """
        if transaction_date is None:
            transaction_date = datetime.now()  # noqa: DTZ005

        transaction = TransactionModel(
            item_name=None,
            transaction_type=TransactionType.CASH_TRANSACTION.value,
            units=None,
            price=price,
            transaction_date=transaction_date
        )
        return self.create(transaction)

    def get_transactions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[TransactionModel]:
        """
        Get transactions within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of transactions in the date range
        """
        return self.session.query(self.model).filter(
            self.model.transaction_date >= start_date,
            self.model.transaction_date <= end_date
        ).order_by(self.model.transaction_date).all()

    def get_transactions_by_item(self, item_name: str) -> list[TransactionModel]:
        """
        Get all transactions for a specific item.

        Args:
            item_name: Name of the item

        Returns:
            List of transactions for the item
        """
        return self.session.query(self.model).filter(
            self.model.item_name == item_name
        ).order_by(self.model.transaction_date).all()

    def calculate_stock_level(
        self,
        item_name: str,
        as_of_date: datetime | None = None
    ) -> int:
        """
        Calculate stock level for an item based on transactions.

        Args:
            item_name: Name of the item
            as_of_date: Date to calculate stock level as of (default: current date)

        Returns:
            Calculated stock level (stock_orders - sales)
        """
        if as_of_date is None:
            as_of_date = datetime.now() # noqa: DTZ005

        # Get all transactions up to the date
        transactions = self.session.query(self.model).filter(
            self.model.item_name == item_name,
            self.model.transaction_date <= as_of_date
        ).all()

        stock_level = 0
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.STOCK_ORDER.value:
                stock_level += transaction.units or 0
            elif transaction.transaction_type == TransactionType.SALE.value:
                stock_level -= transaction.units or 0

        return stock_level

    def get_cash_balance(self, as_of_date: datetime | None = None) -> float:
        """
        Calculate cash balance based on all transactions.

        Args:
            as_of_date: Date to calculate balance as of (default: current date)

        Returns:
            Cash balance (revenue - expenses)
        """
        if as_of_date is None:
            as_of_date = datetime.now() # noqa: DTZ005

        transactions = self.session.query(self.model).filter(
            self.model.transaction_date <= as_of_date
        ).all()

        balance = 0.0
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.SALE.value:
                balance += transaction.price
            elif transaction.transaction_type in (
                TransactionType.STOCK_ORDER.value,
                TransactionType.CASH_TRANSACTION.value
            ):
                balance -= transaction.price

        return balance

    def get_total_revenue(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate total revenue from sales in a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Total revenue
        """
        result = self.session.query(func.sum(self.model.price)).filter(
            self.model.transaction_type == TransactionType.SALE.value,
            self.model.transaction_date >= start_date,
            self.model.transaction_date <= end_date
        ).scalar()

        return float(result) if result else 0.0

    def get_total_expenses(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate total expenses from stock orders and cash transactions.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Total expenses
        """
        result = self.session.query(func.sum(self.model.price)).filter(
            self.model.transaction_type.in_([
                TransactionType.STOCK_ORDER.value,
                TransactionType.CASH_TRANSACTION.value
            ]),
            self.model.transaction_date >= start_date,
            self.model.transaction_date <= end_date
        ).scalar()

        return float(result) if result else 0.0

    def get_top_selling_items(self, limit: int = 10) -> list[dict[str, int | float | str]]:
        """
        Get top selling items by quantity sold.

        Args:
            limit: Number of top items to return

        Returns:
            List of dictionaries with item_name, total_units, and total_revenue
        """
        results = self.session.query(
            self.model.item_name,
            func.sum(self.model.units).label("total_units"),
            func.sum(self.model.price).label("total_revenue")
        ).filter(
            self.model.transaction_type == TransactionType.SALE.value,
            self.model.item_name.isnot(None)
        ).group_by(
            self.model.item_name
        ).order_by(
            func.sum(self.model.units).desc()
        ).limit(limit).all()

        return [
            {
                "item_name": row.item_name,
                "total_units": int(row.total_units or 0),
                "total_revenue": float(row.total_revenue or 0.0)
            }
            for row in results
        ]

    def get_by_transaction_type(
        self,
        transaction_type: str
    ) -> list[TransactionModel]:
        """
        Get all transactions of a specific type.

        Args:
            transaction_type: Type of transaction

        Returns:
            List of transactions of the specified type
        """
        return self.session.query(self.model).filter(
            self.model.transaction_type == transaction_type
        ).order_by(self.model.transaction_date).all()

