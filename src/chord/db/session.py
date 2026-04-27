from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from chord.config import Settings

def make_engine(settings: Settings):
    return create_engine(
        settings.database.url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        future=True,
    )

def make_session_factory(settings: Settings):
    engine = make_engine(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
