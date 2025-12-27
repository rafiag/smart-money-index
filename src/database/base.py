"""Database connection and session management"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings

# SQLAlchemy base class for models
Base = declarative_base()

# Global engine and session factory
_engine = None
_SessionFactory = None


def get_engine():
    """Get or create SQLAlchemy engine (singleton pattern)"""
    global _engine

    if _engine is None:
        settings = get_settings()

        # Engine configuration based on database type
        if settings.database_is_sqlite:
            # SQLite-specific configuration
            _engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.SQL_ECHO,
                connect_args={"check_same_thread": False},  # Allow multi-threading
            )
        else:
            # PostgreSQL configuration
            _engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.SQL_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=True,  # Verify connections before using
            )

    return _engine


def get_session_factory():
    """Get or create session factory (singleton pattern)"""
    global _SessionFactory

    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )

    return _SessionFactory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic cleanup.

    Usage:
        with get_session() as session:
            session.query(Ticker).all()
    """
    SessionFactory = get_session_factory()
    session = SessionFactory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database by creating all tables"""
    from .models import (  # Import here to avoid circular imports
        GoogleTrend,
        InsiderTransaction,
        InstitutionalHolding,
        Price,
        RedditSentiment,
        Ticker,
        ZScore,
    )

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
