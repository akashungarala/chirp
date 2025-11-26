from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.
    """
    # Database settings
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    # Pydantic configuration to read from .env file
    model_config = SettingsConfigDict(env_file=".env")

# Instantiate settings to be imported throughout the app
settings = Settings()