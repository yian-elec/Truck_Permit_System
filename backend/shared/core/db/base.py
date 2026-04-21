"""
base.py - 提供 BaseRepository, Session 管理
定義統一的 CRUD 模板和會話管理
"""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

# 泛型類型變數
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    BaseRepository - 基礎 Repository 類別
    
    提供統一的 CRUD 模板
    負責 session / transaction 管理
    確保所有 DB 錯誤都記錄 log
    """
    
    def __init__(self, model: Type[T]):
        """
        初始化 BaseRepository
        
        Args:
            model: ORM 模型類別
        """
        self.model = model
        self.table_name = model.__tablename__ if hasattr(model, '__tablename__') else model.__name__
    
    def add(self, entity: T) -> T:
        """
        新增一筆資料
        
        Args:
            entity: 要新增的實體
            
        Returns:
            新增後的實體
            
        Raises:
            SQLAlchemyError: 資料庫錯誤
        """
        with get_session() as session:
            try:
                session.add(entity)
                session.flush()  # 獲取 ID 但不提交
                
                # 記錄成功日誌
                entity_id = getattr(entity, 'id', 'unknown')
                logger.db_info(f"Insert success table={self.table_name} id={entity_id}")
                
                return entity
                
            except SQLAlchemyError as e:
                logger.db_error(f"Insert failed table={self.table_name} error={type(e).__name__}")
                raise
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        依據主鍵查詢單筆資料
        
        Args:
            id: 主鍵值
            
        Returns:
            找到的實體，如果不存在則回傳 None
        """
        with get_session() as session:
            try:
                entity = session.query(self.model).filter_by(id=id).first()
                
                if entity:
                    logger.db_info(f"Fetch by id={id} table={self.table_name} result=found")
                else:
                    logger.db_info(f"Fetch by id={id} table={self.table_name} result=not_found")
                
                return entity
                
            except SQLAlchemyError as e:
                logger.db_error(f"Fetch by id failed table={self.table_name} id={id} error={type(e).__name__}")
                raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        查詢多筆資料，可選過濾條件
        
        Args:
            filters: 過濾條件字典
            limit: 限制筆數
            offset: 偏移量
            
        Returns:
            查詢結果列表
        """
        with get_session() as session:
            try:
                query = session.query(self.model)
                
                # 應用過濾條件
                if filters:
                    for key, value in filters.items():
                        if hasattr(self.model, key):
                            if isinstance(value, list):
                                query = query.filter(getattr(self.model, key).in_(value))
                            else:
                                query = query.filter(getattr(self.model, key) == value)
                
                # 應用分頁
                if offset:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                entities = query.all()
                
                # 記錄查詢日誌
                filter_str = str(filters) if filters else "None"
                logger.db_info(f"Query table={self.table_name} filters={filter_str} count={len(entities)}")
                
                return entities
                
            except SQLAlchemyError as e:
                logger.db_error(f"Query failed table={self.table_name} error={type(e).__name__}")
                raise
    
    def update(self, entity: T) -> T:
        """
        更新一筆資料
        
        Args:
            entity: 要更新的實體
            
        Returns:
            更新後的實體
            
        Raises:
            SQLAlchemyError: 資料庫錯誤
        """
        with get_session() as session:
            try:
                # 合併實體到會話中
                merged_entity = session.merge(entity)
                session.flush()
                
                # 記錄成功日誌
                entity_id = getattr(merged_entity, 'id', 'unknown')
                logger.db_info(f"Update success table={self.table_name} id={entity_id}")
                
                return merged_entity
                
            except SQLAlchemyError as e:
                entity_id = getattr(entity, 'id', 'unknown')
                logger.db_error(f"Update failed table={self.table_name} id={entity_id} error={type(e).__name__}")
                raise
    
    def delete(self, id: Any) -> bool:
        """
        刪除一筆資料
        
        Args:
            id: 主鍵值
            
        Returns:
            是否刪除成功
            
        Raises:
            SQLAlchemyError: 資料庫錯誤
        """
        with get_session() as session:
            try:
                entity = session.query(self.model).filter_by(id=id).first()
                if entity:
                    session.delete(entity)
                    session.flush()
                    
                    logger.db_info(f"Delete success table={self.table_name} id={id}")
                    return True
                else:
                    logger.db_info(f"Delete failed table={self.table_name} id={id} reason=not_found")
                    return False
                    
            except SQLAlchemyError as e:
                logger.db_error(f"Delete failed table={self.table_name} id={id} error={type(e).__name__}")
                raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        計算符合條件的記錄數量
        
        Args:
            filters: 過濾條件字典
            
        Returns:
            記錄數量
        """
        with get_session() as session:
            try:
                query = session.query(self.model)
                
                # 應用過濾條件
                if filters:
                    for key, value in filters.items():
                        if hasattr(self.model, key):
                            if isinstance(value, list):
                                query = query.filter(getattr(self.model, key).in_(value))
                            else:
                                query = query.filter(getattr(self.model, key) == value)
                
                count = query.count()
                
                # 記錄查詢日誌
                filter_str = str(filters) if filters else "None"
                logger.db_info(f"Count table={self.table_name} filters={filter_str} count={count}")
                
                return count
                
            except SQLAlchemyError as e:
                logger.db_error(f"Count failed table={self.table_name} error={type(e).__name__}")
                raise
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        檢查是否存在符合條件的記錄
        
        Args:
            filters: 過濾條件字典
            
        Returns:
            是否存在
        """
        return self.count(filters) > 0
    
    def get_session(self):
        """
        取得資料庫會話 context manager (用於複雜查詢)
        
        Returns:
            資料庫會話 context manager
        """
        return get_session()
