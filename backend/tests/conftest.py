import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
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

@pytest.fixture(scope="function")
def engine():
    connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else None,
    )
    # We still use drop_all/create_all for per-test isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    # Register and login a test user
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    client.post("/auth/register", json=user_data)
    
    # Login manually via form data
    response = client.post("/auth/login", data={"username": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
