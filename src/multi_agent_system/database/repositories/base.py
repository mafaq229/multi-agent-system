"""
Base repository pattern with common CRUD operations.

This provides a generic repository implementation that can be extended
for specific models.
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from multi_agent_system.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository with common database operations.

    Provides generic CRUD operations (Create, Read, Update, Delete),
    bulk operations, query filtering and pagination, with type safety
    using Generic typing.

    Attributes:
        model: SQLAlchemy model class
        session: Database session

    Example Usage:
    ```python
    # Create repository
    inventory_repo = BaseRepository(InventoryModel, session)

    # Get by ID
    item = inventory_repo.get_by_id(1)

    # Check if exists
    if inventory_repo.exists(1):
        # Create new item
        new_item = InventoryModel(item_name="A4 paper", unit_price=0.05)
        created = inventory_repo.create(new_item)

        # Create multiple items
        items = [
            InventoryModel(item_name="A4 paper", unit_price=0.05),
            InventoryModel(item_name="Glossy paper", unit_price=0.08),
        ]
        created_items = inventory_repo.create_many(items)

        # Update
        created.unit_price = 0.06
        updated = inventory_repo.update(created)

        # Delete
        inventory_repo.delete(1)

        # Delete multiple
        deleted_count = inventory_repo.delete_many([2, 3, 4])
    ```
    """

    def __init__(self, model: type[ModelType], session: Session):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> ModelType | None:
        """Get record by ID."""
        return self.session.query(self.model).filter(self.model.id == id).first()  # type: ignore[attr-defined]

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[ModelType]:
        """Get all records with pagination."""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        self.session.merge(obj)
        self.session.flush()
        return obj

    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def count(self) -> int:
        """Count total records."""
        return self.session.query(self.model).count()

    def create_many(self, objs: list[ModelType]) -> list[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            objs: List of model instances to create

        Returns:
            List of created model instances
        """
        self.session.add_all(objs)
        self.session.flush()
        for obj in objs:
            self.session.refresh(obj)
        return objs

    def delete_many(self, ids: list[int]) -> int:
        """
        Delete multiple records by IDs.

        Args:
            ids: List of record IDs to delete

        Returns:
            Number of records deleted
        """
        deleted_count = 0
        for id_val in ids:
            if self.delete(id_val):
                deleted_count += 1
        return deleted_count

    def exists(self, id: int) -> bool:
        """
        Check if a record exists by ID.

        Args:
            id: Record ID to check

        Returns:
            True if record exists, False otherwise
        """
        return self.get_by_id(id) is not None

