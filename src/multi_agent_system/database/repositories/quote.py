"""Quote repository with quote management queries."""

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from multi_agent_system.database.models import QuoteModel
from multi_agent_system.database.repositories.base import BaseRepository


class QuoteRepository(BaseRepository[QuoteModel]):
    """
    Repository for quote operations.

    Extends BaseRepository with quote-specific methods for managing
    quotes, searching, and statistics.
    """

    def __init__(self, session: Session):
        """Initialize repository with session."""
        super().__init__(QuoteModel, session)

    def get_by_quote_id(self, quote_id: str) -> QuoteModel | None:
        """
        Get quote by unique quote identifier.

        Args:
            quote_id: Unique quote identifier

        Returns:
            Quote model or None if not found
        """
        return self.session.query(self.model).filter(
            self.model.quote_id == quote_id
        ).first()

    def get_by_customer(self, customer_id: str) -> list[QuoteModel]:
        """
        Get all quotes for a customer.

        Args:
            customer_id: Customer identifier

        Returns:
            List of quotes for the customer
        """
        return self.session.query(self.model).filter(
            self.model.customer_id == customer_id
        ).all()

    def get_pending_quotes(self) -> list[QuoteModel]:
        """Get all pending quotes."""
        return self.session.query(self.model).filter(
            self.model.status == "pending"
        ).all()

    def get_expired_quotes(self, as_of_date: datetime | None = None) -> list[QuoteModel]:
        """
        Get all expired quotes.

        Args:
            as_of_date: Date to check expiration against (default: current date)

        Returns:
            List of expired quotes
        """
        if as_of_date is None:
            as_of_date = datetime.now() # noqa: DTZ005
        return self.session.query(self.model).filter(
            self.model.valid_until < as_of_date
        ).all()

    def update_quote_status(
        self,
        quote_id: str,
        status: str
    ) -> QuoteModel | None:
        """
        Update the status of a quote.

        Args:
            quote_id: Unique quote identifier
            status: New status

        Returns:
            Updated quote model or None if not found
        """
        quote = self.get_by_quote_id(quote_id)
        if quote:
            quote.status = status
            self.session.flush()
            self.session.refresh(quote)
        return quote

    def search_quotes(self, search_terms: list[str]) -> list[QuoteModel]:
        """
        Search quotes by multiple terms.

        Searches in quote_id, customer_id, and quote_explanation fields.

        Args:
            search_terms: List of search terms

        Returns:
            List of matching quotes
        """
        if not search_terms:
            return []

        conditions = []
        for term in search_terms:
            term_pattern = f"%{term}%"
            conditions.append(
                or_(
                    self.model.quote_id.ilike(term_pattern),
                    self.model.customer_id.ilike(term_pattern),
                    self.model.quote_explanation.ilike(term_pattern)
                )
            )

        return self.session.query(self.model).filter(
            or_(*conditions)
        ).all()

    def get_by_status(self, status: str) -> list[QuoteModel]:
        """
        Get all quotes with a specific status.

        Args:
            status: Quote status

        Returns:
            List of quotes with the specified status
        """
        return self.session.query(self.model).filter(
            self.model.status == status
        ).all()

    def get_quote_statistics(self) -> dict[str, int | float]:
        """
        Get quote statistics.

        Returns:
            Dictionary with statistics:
            - total_quotes: Total number of quotes
            - pending_count: Number of pending quotes
            - accepted_count: Number of accepted quotes
            - rejected_count: Number of rejected quotes
            - expired_count: Number of expired quotes
            - total_value: Total value of all quotes
            - average_value: Average quote value
        """
        total_quotes = self.count()
        pending_count = len(self.get_pending_quotes())
        expired_count = len(self.get_expired_quotes())

        # Get quotes by status
        accepted_quotes = self.get_by_status("accepted")
        rejected_quotes = self.get_by_status("rejected")

        # Calculate totals
        all_quotes = self.get_all(limit=10000)  # Get all quotes
        total_value = sum(quote.total_amount for quote in all_quotes)
        average_value = total_value / total_quotes if total_quotes > 0 else 0.0

        return {
            "total_quotes": total_quotes,
            "pending_count": pending_count,
            "accepted_count": len(accepted_quotes),
            "rejected_count": len(rejected_quotes),
            "expired_count": expired_count,
            "total_value": total_value,
            "average_value": average_value,
        }

