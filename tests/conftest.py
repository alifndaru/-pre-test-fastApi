import asyncio
import pytest
import pytest_asyncio
import warnings
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_async_session, Base
from app.models import User, Task

# Test database URL - menggunakan SQLite untuk testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine dengan SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
)

test_async_session = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_async_session():
    async with test_async_session() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Setup test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(setup_database):
    """Create test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session(setup_database):
    """Create test database session"""
    async with test_async_session() as session:
        yield session