from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction

from app.config import settings
from app.db import get_session
from app.main import app
from app.models.base import Base

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}"


@pytest.fixture
async def ac() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="https://test") as c:
        yield c


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
    conn = engine.connect()
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    conn.execute(text("commit"))
    conn.execute(text("create database test"))
    conn.close()

    yield

    conn = engine.connect()
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db: Generator) -> Generator:
    engine = create_engine(f"{DATABASE_URL.replace('+asyncpg', '')}/test")

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)


@pytest.fixture
async def session() -> AsyncGenerator:
    async_engine = create_async_engine(f"{DATABASE_URL}/test")
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
            future=True,
        )

        async_session = AsyncSessionLocal()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session: Session, transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        def test_get_session() -> Generator:
            try:
                yield AsyncSessionLocal
            except SQLAlchemyError:
                pass

        app.dependency_overrides[get_session] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()
