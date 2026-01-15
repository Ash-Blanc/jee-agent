"""
Centralized database configuration for JEE Agent.

This module provides all database access for the application:
- PostgresDb for agent sessions and memory
- PgVector for knowledge base vector search
- StudentStorage for custom student state management
"""

from typing import Optional, Dict, Any
from functools import lru_cache

from sqlalchemy import create_engine, text, Table, Column, String, select
from sqlalchemy.schema import MetaData
from sqlalchemy.dialects.postgresql import JSONB

from agno.db.postgres import PostgresDb
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.embedder.mistral import MistralEmbedder

from jee_agent.config.settings import DATABASE_URL, EMBEDDING_MODEL


# Schema version for future migrations
SCHEMA_VERSION = "1.0.0"

# SQLAlchemy metadata (shared across all tables)
metadata = MetaData()


@lru_cache(maxsize=1)
def get_engine():
    """Get the SQLAlchemy engine (lazy singleton)."""
    return create_engine(DATABASE_URL)


@lru_cache(maxsize=1)
def get_agent_db(session_table: str = "jee_sessions") -> PostgresDb:
    """
    Get a PostgresDb instance for agent sessions and memory.
    
    Args:
        session_table: Name of the session table to use
        
    Returns:
        Configured PostgresDb instance
    """
    return PostgresDb(
        db_url=DATABASE_URL,
        session_table=session_table,
    )


@lru_cache(maxsize=1)
def get_vector_db(table_name: str = "jee_pyqs") -> PgVector:
    """
    Get a PgVector instance for knowledge base vector search.
    
    Args:
        table_name: Name of the vector table to use
        
    Returns:
        Configured PgVector instance with hybrid search
    """
    return PgVector(
        db_url=DATABASE_URL,
        table_name=table_name,
        search_type=SearchType.hybrid,
        embedder=MistralEmbedder(id=EMBEDDING_MODEL),
    )


class StudentStorage:
    """PostgreSQL-based student data storage using JSONB."""
    
    def __init__(self):
        self.engine = get_engine()
        
        # Define table with PostgreSQL JSONB for efficient querying
        self.students = Table(
            "students",
            metadata,
            Column("student_id", String, primary_key=True),
            Column("data", JSONB),  # JSONB for better indexing and querying
            extend_existing=True,
        )
        
        self._init_db()

    def _init_db(self):
        metadata.create_all(self.engine)

    def get(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as conn:
            stmt = select(self.students.c.data).where(
                self.students.c.student_id == student_id
            )
            result = conn.execute(stmt).fetchone()
            if result:
                return result[0]
            return None

    def get_last_student(self) -> Optional[Dict[str, Any]]:
        """Get the most recently active student (or any if only one exists)"""
        with self.engine.connect() as conn:
            # Just get the first one for now as it's primarily a single-user tool
            stmt = select(self.students.c.data).limit(1)
            result = conn.execute(stmt).fetchone()
            if result:
                return result[0]
            return None

    def upsert(self, student_id: str, data: Dict[str, Any]):
        with self.engine.connect() as conn:
            # Check if exists
            stmt = select(self.students.c.student_id).where(
                self.students.c.student_id == student_id
            )
            exists = conn.execute(stmt).fetchone()
            
            if exists:
                stmt = (
                    self.students.update()
                    .where(self.students.c.student_id == student_id)
                    .values(data=data)
                )
            else:
                stmt = self.students.insert().values(
                    student_id=student_id, data=data
                )
            
            conn.execute(stmt)
            conn.commit()

    def clear(self):
        """Clear all student data"""
        with self.engine.connect() as conn:
            conn.execute(self.students.delete())
            conn.commit()


def validate_connection() -> bool:
    """
    Validate database connection on startup.
    
    Returns:
        True if connection is successful
        
    Raises:
        RuntimeError: If connection fails
    """
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to connect to PostgreSQL database: {e}") from e


def ensure_schema():
    """
    Ensure database schema is up to date.
    Creates tables if they don't exist.
    """
    metadata.create_all(get_engine())


# Module-level aliases for convenience (lazy via lru_cache)
agent_db = get_agent_db()
vector_db = get_vector_db()


__all__ = [
    "agent_db",
    "vector_db", 
    "get_engine",
    "metadata",
    "get_agent_db",
    "get_vector_db",
    "validate_connection",
    "ensure_schema",
    "StudentStorage",
    "DATABASE_URL",
    "SCHEMA_VERSION",
]
