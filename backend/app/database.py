from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Connection string for the Postgres service running in Docker
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/teste_tecnico"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
