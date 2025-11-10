"""Quote request repository."""

from sqlalchemy.orm import Session

from multi_agent_system.database.models import QuoteRequestModel
from multi_agent_system.database.repositories.base import BaseRepository


class QuoteRequestRepository(BaseRepository[QuoteRequestModel]):
    """
    Repository for quote request operations.

    Extends BaseRepository with quote request-specific methods for
    managing customer quote inquiries.
    """

    def __init__(self, session: Session):
        """Initialize repository with session."""
        super().__init__(QuoteRequestModel, session)

    def create_request(
        self,
        customer_id: str,
        request_text: str,
        status: str = "pending"
    ) -> QuoteRequestModel:
        """
        Create a new quote request.

        Args:
            customer_id: Customer identifier
            request_text: Original request text
            status: Request status (default: "pending")

        Returns:
            Created quote request model
        """
        request = QuoteRequestModel(
            customer_id=customer_id,
            request_text=request_text,
            status=status
        )
        return self.create(request)

    def get_pending_requests(self) -> list[QuoteRequestModel]:
        """Get all pending quote requests."""
        return self.session.query(self.model).filter(
            self.model.status == "pending"
        ).all()

    def update_request_status(
        self,
        request_id: int,
        status: str
    ) -> QuoteRequestModel | None:
        """
        Update the status of a quote request.

        Args:
            request_id: Request ID
            status: New status

        Returns:
            Updated quote request model or None if not found
        """
        request = self.get_by_id(request_id)
        if request:
            request.status = status
            self.session.flush()
            self.session.refresh(request)
        return request

    def get_by_customer(self, customer_id: str) -> list[QuoteRequestModel]:
        """
        Get all quote requests for a customer.

        Args:
            customer_id: Customer identifier

        Returns:
            List of quote requests for the customer
        """
        return self.session.query(self.model).filter(
            self.model.customer_id == customer_id
        ).all()

    def get_by_status(self, status: str) -> list[QuoteRequestModel]:
        """
        Get all quote requests with a specific status.

        Args:
            status: Request status

        Returns:
            List of quote requests with the specified status
        """
        return self.session.query(self.model).filter(
            self.model.status == status
        ).all()

