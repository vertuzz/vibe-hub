import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool, NullPool
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Ensure app is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.models import Base
from app.database import get_db

# Use environment variable for test DB or default to in-memory SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")

# Convert to async URL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite://"):
    ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if not SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        yield
        return

    # For PostgreSQL, we need to create the database if it doesn't exist
    # First, connect to the default 'postgres' database to run CREATE/DROP
    base_url = SQLALCHEMY_DATABASE_URL.rsplit("/", 1)[0]
    db_name = SQLALCHEMY_DATABASE_URL.rsplit("/", 1)[1]
    
    # Connect to 'postgres' database
    admin_url = f"{base_url}/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    with admin_engine.connect() as conn:
        # Terminate other sessions if they exist (to allow DROP DATABASE)
        conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
              AND pid <> pg_backend_pid();
        """))
        conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        conn.execute(text(f"CREATE DATABASE {db_name}"))
    
    yield
    
    # Disconnect following engine dispose to allow drop
    with admin_engine.connect() as conn:
        conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
              AND pid <> pg_backend_pid();
        """))
        conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    admin_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def engine():
    if ASYNC_DATABASE_URL.startswith("sqlite"):
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            poolclass=NullPool,
        )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session
            
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_headers(client):
    # Register and login a test user
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    await client.post("/auth/register", json=user_data)
    
    # Login manually via form data
    response = await client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
