"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from ..core.config import get_settings
from .models import Base

settings = get_settings()

# Create engine with appropriate pooling for SQLite or PostgreSQL
engine_kwargs = {
    "pool_pre_ping": True,  # Test connections before use
    "echo": False,  # Set to True for SQL logging
}

# Use StaticPool for SQLite, QueuePool for PostgreSQL
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["poolclass"] = StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 40

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for database session in FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def drop_all_tables():
    """Drop all tables (development only)"""
    Base.metadata.drop_all(bind=engine)
