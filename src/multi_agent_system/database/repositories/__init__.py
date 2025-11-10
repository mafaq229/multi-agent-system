"""Repository pattern implementation for data access."""

from multi_agent_system.database.repositories.base import BaseRepository
from multi_agent_system.database.repositories.inventory import InventoryRepository
from multi_agent_system.database.repositories.quote import QuoteRepository
from multi_agent_system.database.repositories.quote_request import QuoteRequestRepository
from multi_agent_system.database.repositories.transaction import TransactionRepository

__all__ = [
    "BaseRepository",
    "InventoryRepository",
    "QuoteRepository",
    "QuoteRequestRepository",
    "TransactionRepository",
]

