"""Financial reporting service."""

from datetime import datetime
from typing import Any

from multi_agent_system.database.repositories.inventory import InventoryRepository
from multi_agent_system.database.repositories.transaction import TransactionRepository
from multi_agent_system.domain.models import FinancialReport


class FinancialService:
    """
    Service for financial reporting and analysis.

    Handles financial calculations including cash balance, revenue, expenses,
    profit, and comprehensive financial reports.

    Example Usage:
    ```python
    financial_service = FinancialService(transaction_repo, inventory_repo)

    # Get cash balance
    balance = financial_service.get_cash_balance(datetime.now()) # noqa: DTZ005

    # Generate comprehensive report
    report = financial_service.generate_financial_report(datetime.now())
    ```
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        inventory_repository: InventoryRepository
    ):
        """
        Initialize financial service.

        Args:
            transaction_repository: Repository for transaction data access
            inventory_repository: Repository for inventory data access
        """
        self.transaction_repo = transaction_repository
        self.inventory_repo = inventory_repository

    def get_cash_balance(self, as_of_date: datetime) -> float:
        """
        Get cash balance as of a specific date.

        Args:
            as_of_date: Date to calculate balance as of

        Returns:
            Cash balance (revenue - expenses)
        """
        return self.transaction_repo.get_cash_balance(as_of_date)

    def get_inventory_value(self,) -> float:
        """
        Get total inventory value.

        Returns:
            Total inventory value (sum of current_stock * unit_price)
        """
        return self.inventory_repo.get_inventory_value()

    def generate_financial_report(self, as_of_date: datetime) -> FinancialReport:
        """
        Generate comprehensive financial report.

        Args:
            as_of_date: Date to generate report as of

        Returns:
            FinancialReport with complete financial data
        """
        # Get cash balance
        cash_balance = self.get_cash_balance(as_of_date)

        # Get inventory value
        inventory_value = self.get_inventory_value()

        # Calculate total assets
        total_assets = cash_balance + inventory_value

        # Get inventory summary
        inventory_items = self.inventory_repo.get_all(limit=10000)
        inventory_summary = [
            {
                "item_name": item.item_name,
                "category": item.category,
                "current_stock": item.current_stock,
                "unit_price": item.unit_price,
                "total_value": item.current_stock * item.unit_price,
                "min_stock_level": item.min_stock_level,
                "needs_reorder": item.current_stock <= item.min_stock_level
            }
            for item in inventory_items
        ]

        # Get top selling products
        top_selling_products = self.get_top_selling_products(limit=10)

        # Calculate revenue and expenses for the year
        # Using start of year to as_of_date
        year_start = as_of_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        total_revenue = self.get_total_revenue(year_start, as_of_date)
        total_expenses = self.get_total_expenses(year_start, as_of_date)
        net_profit = self.get_net_profit(year_start, as_of_date)

        return FinancialReport(
            as_of_date=as_of_date,
            cash_balance=cash_balance,
            inventory_value=inventory_value,
            total_assets=total_assets,
            inventory_summary=inventory_summary,
            top_selling_products=top_selling_products,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit
        )

    def get_total_revenue(self, start_date: datetime, end_date: datetime) -> float:
        """
        Calculate total revenue from sales in a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Total revenue
        """
        return self.transaction_repo.get_total_revenue(start_date, end_date)

    def get_total_expenses(self, start_date: datetime, end_date: datetime) -> float:
        """
        Calculate total expenses in a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Total expenses
        """
        return self.transaction_repo.get_total_expenses(start_date, end_date)

    def get_net_profit(self, start_date: datetime, end_date: datetime) -> float:
        """
        Calculate net profit (revenue - expenses) in a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Net profit
        """
        revenue = self.get_total_revenue(start_date, end_date)
        expenses = self.get_total_expenses(start_date, end_date)
        return revenue - expenses

    def get_top_selling_products(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get top selling products by quantity sold.

        Args:
            limit: Number of top products to return

        Returns:
            List of dictionaries with product information
        """
        return self.transaction_repo.get_top_selling_items(limit)

