"""
core/db - 資料庫管理模組
提供資料庫連線、Repository 基礎類別和初始化功能
"""

from .connection import (
    DatabaseConnection,
    db_connection,
    get_engine,
    get_async_engine,
    get_session,
    get_async_session,
    Base
)
from .base import BaseRepository
from .init_db import init_db, DatabaseInitializer

__all__ = [
    "DatabaseConnection",
    "db_connection",
    "get_engine",
    "get_async_engine", 
    "get_session",
    "get_async_session",
    "Base",
    "BaseRepository",
    "init_db",
    "DatabaseInitializer"
]
