"""
db_config.py - 資料庫相關設定
管理 PostgreSQL 資料庫連線設定
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .env_file_path import backend_env_file


class DatabaseConfig(BaseSettings):
    """
    資料庫設定類別
    管理 PostgreSQL 資料庫連線設定

    注意：不可用欄位名 `user`，否則 pydantic-settings 會綁定 POSIX 環境變數 USER，
    覆寫 .env 的 DB_USER。
    """

    model_config = SettingsConfigDict(
        env_file=backend_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="localhost", validation_alias="DB_HOST")
    port: int = Field(default=5432, validation_alias="DB_PORT")
    db_user: str = Field(default="postgres", validation_alias="DB_USER")
    password: str = Field(default="postgres", validation_alias="DB_PASSWORD")
    name: str = Field(default="base_project", validation_alias="DB_NAME")

    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, validation_alias="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, validation_alias="DB_POOL_RECYCLE")

    echo: bool = Field(default=False, validation_alias="DB_ECHO")
    echo_pool: bool = Field(default=False, validation_alias="DB_ECHO_POOL")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )
