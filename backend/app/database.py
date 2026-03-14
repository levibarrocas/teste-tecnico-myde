from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .core.config import settings

# Use the URL from the settings object, which is loaded from environment variables.
# This is the single source of truth for the database connection.
engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
