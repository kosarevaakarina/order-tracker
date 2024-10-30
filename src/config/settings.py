import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class DatabaseSettings(BaseSettings):
    user: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    password: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "postgres"))
    database: str = Field(default_factory=lambda: os.getenv("POSTGRES_DATABASE", "postgres"))
    host: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = Field(default_factory=lambda: os.getenv("POSTGRES_PORT", 5432))

    @property
    def url(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'

    @property
    def url_sync(self):
        return f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'


class AppSettings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    title: str = "Order Tracker"