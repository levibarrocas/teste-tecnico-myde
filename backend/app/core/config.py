from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "TEST_SECRET_KEY_PLEASE_CHANGE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str
    
    # AWS / LocalStack Settings
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"
    SQS_ENDPOINT_URL: str
    SQS_QUEUE_NAME: str = "proposals-queue"
    MOCK_BANK_URL: str

    # By not specifying env_file, we rely solely on environment variables
    model_config = SettingsConfigDict()

settings = Settings()
