"""
connection.py - 建立資料庫連線
提供資料庫引擎和會話管理
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager

from shared.core.config import settings
from shared.core.logger.logger import logger

# 建立 Base 類別
Base = declarative_base()


class DatabaseConnection:
    """
    資料庫連線管理類別
    負責建立和管理資料庫引擎和會話
    """
    
    def __init__(self):
        """初始化資料庫連線"""
        self._engine: Engine = None
        self._async_engine: AsyncEngine = None
        self._session_factory = None
        self._async_session_factory = None
        self._initialized = False
    
    def _create_engines(self):
        """建立資料庫引擎"""
        try:
            # 同步引擎
            self._engine = create_engine(
                settings.database.database_url,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_timeout=settings.database.pool_timeout,
                pool_recycle=settings.database.pool_recycle,
                echo=settings.database.echo,
                echo_pool=settings.database.echo_pool
            )
            
            # 異步引擎
            self._async_engine = create_async_engine(
                settings.database.async_database_url,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_timeout=settings.database.pool_timeout,
                pool_recycle=settings.database.pool_recycle,
                echo=settings.database.echo,
                echo_pool=settings.database.echo_pool
            )
            
            # 會話工廠
            self._session_factory = sessionmaker(bind=self._engine)
            self._async_session_factory = async_sessionmaker(bind=self._async_engine)
            
            self._initialized = True
            
            logger.db_info(
                f"Connection established host={settings.database.host} "
                f"db={settings.database.name}"
            )
            
        except Exception as e:
            logger.db_error(f"Connection failed - {str(e)}")
            raise
    
    def get_engine(self) -> Engine:
        """
        取得同步資料庫引擎
        
        Returns:
            同步資料庫引擎
        """
        if not self._initialized:
            self._create_engines()
        return self._engine
    
    def get_async_engine(self) -> AsyncEngine:
        """
        取得異步資料庫引擎
        
        Returns:
            異步資料庫引擎
        """
        if not self._initialized:
            self._create_engines()
        return self._async_engine
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        取得同步資料庫會話 (Context Manager)
        
        Yields:
            同步資料庫會話
        """
        if not self._initialized:
            self._create_engines()
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.db_error(f"Transaction rollback - {str(e)}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        取得異步資料庫會話 (Async Context Manager)
        
        Yields:
            異步資料庫會話
        """
        if not self._initialized:
            self._create_engines()
        
        session = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.db_error(f"Transaction rollback - {str(e)}")
            raise
        finally:
            await session.close()
    
    def close(self):
        """關閉資料庫連線"""
        if self._engine:
            self._engine.dispose()
        if self._async_engine:
            # 注意：異步引擎需要在事件循環中關閉
            pass


# 全域資料庫連線實例
db_connection = DatabaseConnection()


def get_engine() -> Engine:
    """
    取得同步資料庫引擎
    
    Returns:
        同步資料庫引擎
    """
    return db_connection.get_engine()


def get_async_engine() -> AsyncEngine:
    """
    取得異步資料庫引擎
    
    Returns:
        異步資料庫引擎
    """
    return db_connection.get_async_engine()


def get_session() -> Generator[Session, None, None]:
    """
    取得同步資料庫會話 (Context Manager)
    
    Yields:
        同步資料庫會話
    """
    return db_connection.get_session()


def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    取得異步資料庫會話 (Async Context Manager)
    
    Yields:
        異步資料庫會話
    """
    return db_connection.get_async_session()
