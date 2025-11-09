"""
Database connection and session management.

This module handles database connections, session lifecycle, and provides
utilities for database initialization.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, cast

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from multi_agent_system.database.models import Base

# Global session factory
_session_factory: sessionmaker | None = None
_engine: Engine | None = None


def create_db_engine(database_url: str, echo: bool = False) -> Engine:
    """
    Create database engine with appropriate configuration.

    Requirements:
    1. Support SQLite for development and PostgreSQL for production
    2. Configure connection pooling
    3. Enable query echoing for debugging
    4. Add connection validation
    5. Handle SQLite-specific configuration (foreign keys)

    Args:
        database_url: Database connection URL
        echo: If True, log all SQL queries

    Returns:
        SQLAlchemy engine

    Expected Input: "sqlite:///./munder_difflin.db", echo=False
    Expected Output: Configured SQLAlchemy engine
    """
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        engine = create_engine(
            database_url,
            echo=echo,
            connect_args=connect_args,
            poolclass=StaticPool,  # Use static pool for SQLite
        )

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn: Any, _connection_record: Any) -> None:
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        engine = create_engine(
            database_url,
            echo=echo,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before use
        )
    return engine


def init_database(database_url: str, echo: bool = False) -> Engine:
    """
    Initialize database and create all tables.

    Steps:
    1. Create engine
    2. Create all tables from Base.metadata
    3. Set up global session factory
    4. Return engine for further use

    Args:
        database_url: Database connection URL
        echo: If True, log all SQL queries

    Returns:
        Database engine

    Expected Input: "sqlite:///./munder_difflin.db"
    Expected Output: Initialized engine
    """
    global _engine, _session_factory  # ensure we update the module-level engine and session factory

    # Create engine
    _engine = create_db_engine(database_url, echo)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    # Create session factory
    _session_factory = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    return _engine


def get_session() -> Session:
    """
    Get a new database session.

    Returns:
        Database session

    Raises:
        RuntimeError: If database not initialized

    Expected Output: SQLAlchemy Session object
    """
    if _session_factory is None:
        msg = "Database not initialized. Call init_database() first."
        raise RuntimeError(msg)
    return cast(Session, _session_factory())


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic commit/rollback.

    This provides a transactional scope for database operations with
    automatic error handling and cleanup.

    Yields:
        Database session

    Example Usage:
    ```python
    with session_scope() as session:
        item = session.query(InventoryModel).filter_by(id=1).first()
        item.current_stock += 100
        # Automatically commits on success, rolls back on error
    ```
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def close_database() -> None:
    """
    Close database connection and clean up resources.
    """
    global _engine, _session_factory

    if _engine:
        _engine.dispose()
        _engine = None

    _session_factory = None


# TODO: Add utility functions
# Examples:
# - def check_connection() -> bool: Test database connectivity
# - def get_engine() -> Engine: Get the global engine
# - async def get_async_session() -> AsyncSession: For async operations

