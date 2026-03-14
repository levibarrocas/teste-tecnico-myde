from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "TEST_SECRET_KEY_PLEASE_CHANGE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/teste_tecnico"
    
    # AWS / LocalStack Settings
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"
    SQS_ENDPOINT_URL: str = "http://localhost:4566"
    SQS_QUEUE_NAME: str = "proposals-queue"
    MOCK_BANK_URL: str = "http://localhost:8001"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
