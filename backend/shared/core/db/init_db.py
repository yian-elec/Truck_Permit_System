"""
init_db.py - 初始化流程
建立 DB / 建立 Table / 匯入 seed
"""

import os
import sys
import importlib
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from shared.core.config import settings
from shared.core.logger.logger import logger
from shared.core.db.connection import get_engine


class DatabaseInitializer:
    """
    資料庫初始化器
    負責建立資料庫、資料表和匯入初始資料
    """
    
    def __init__(self):
        """初始化資料庫初始化器"""
        self.engine = None
        self.contexts_path = Path("src/contexts")
        # False 時已自 metadata 移除 routing.*，且跳過 routing_restriction seed
        self._postgis_available: bool = True
    
    def init_database(self) -> bool:
        """
        初始化資料庫
        
        Returns:
            是否初始化成功
        """
        try:
            logger.db_info("Starting database initialization...")
            
            # 1. 建立資料庫 (若不存在)
            self._create_database_if_not_exists()
            
            # 2. 建立資料表
            self._create_tables()
            
            # 3. 匯入 seed 資料
            self._import_seed_data()

            # 4. development：可選建立後台 Dev 管理員（見 iam.infra.dev_admin_bootstrap）
            self._ensure_dev_iam_admin()
            
            logger.db_info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.db_error(f"Database initialization failed - {str(e)}")
            return False

    @staticmethod
    def _ensure_dev_iam_admin() -> None:
        try:
            from src.contexts.iam.infra.dev_admin_bootstrap import (
                ensure_dev_iam_admin_if_configured,
            )

            ensure_dev_iam_admin_if_configured()
        except Exception as exc:
            logger.db_warning(f"Dev IAM admin bootstrap failed (non-fatal): {exc}")
    
    def _create_database_if_not_exists(self):
        """建立資料庫 (若不存在)"""
        try:
            # 使用 postgres 預設資料庫連線
            db_config = settings.database
            postgres_url = (
                f"postgresql://{db_config.db_user}:{db_config.password}"
                f"@{db_config.host}:{db_config.port}/postgres"
            )
            
            # 建立連線到 postgres 資料庫
            postgres_engine = create_engine(postgres_url)
            
            with postgres_engine.connect() as conn:
                # 檢查資料庫是否存在
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": db_config.name})
                
                if not result.fetchone():
                    # 建立資料庫
                    conn.execute(text("COMMIT"))  # 結束當前事務
                    conn.execute(text(f"CREATE DATABASE {db_config.name}"))
                    logger.db_info(f"Database {db_config.name} created")
                else:
                    logger.db_info(f"Database {db_config.name} already exists")
            
            postgres_engine.dispose()
            
        except SQLAlchemyError as e:
            logger.db_error(f"Failed to create database - {str(e)}")
            raise
    
    def _create_tables(self):
        """建立資料表"""
        try:
            # 取得主引擎
            self.engine = get_engine()
            
            # 掃描所有 context 的 schema
            schema_modules = self._scan_schema_modules()
            
            if not schema_modules:
                logger.db_info("No schema modules found")
                return
            
            # 匯入所有 schema 模組
            for module_path in schema_modules:
                self._import_schema_module(module_path)

            # PostgreSQL named schema（例如 Integration_Operations 的 ops.* 資料表）
            from sqlalchemy import text

            # PostGIS 必須獨立交易：若在同一交易中 CREATE EXTENSION 失敗，PG 會中止該交易，
            # 導致後續 CREATE SCHEMA 全部失敗（InFailedSqlTransaction）。
            postgis_available = self.engine.dialect.name != "postgresql"
            if self.engine.dialect.name == "postgresql":
                postgis_available = False
                try:
                    with self.engine.begin() as conn:
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                    postgis_available = True
                except Exception as e:
                    logger.db_warning(
                        "PostGIS extension could not be enabled "
                        f"({e!s}). "
                        "將略過 routing.*（geometry 欄位）建表與 seed；"
                        "若需路線／限制功能請在 PostgreSQL 主機安裝 PostGIS（例："
                        "Ubuntu/Pop!_OS：`sudo apt install postgresql-16-postgis-3`）。"
                    )

            self._postgis_available = postgis_available

            # 無 PostGIS 時 geometry 型別不存在，create_all 會失敗；改為不建立 routing schema 下之表。
            if self.engine.dialect.name == "postgresql" and not postgis_available:
                from shared.core.db.connection import Base

                routing_tables = [
                    t
                    for t in Base.metadata.sorted_tables
                    if getattr(t, "schema", None) == "routing"
                ]
                for t in reversed(routing_tables):
                    Base.metadata.remove(t)
                logger.db_warning(
                    "PostGIS 不可用：已跳過 routing.* 資料表 DDL；其餘 schema 仍會建立。"
                )

            with self.engine.begin() as conn:
                if conn.dialect.name == "postgresql":
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS ops"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS application"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS routing"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS review"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS permit"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS page_model"))
                    conn.execute(text("CREATE SCHEMA IF NOT EXISTS iam"))
            
            # 建立所有資料表
            from shared.core.db.connection import Base
            Base.metadata.create_all(bind=self.engine)

            # create_all 不會為既有表補新欄位：routing 增量欄位以 IF NOT EXISTS 補齊
            if self.engine.dialect.name == "postgresql" and self._postgis_available:
                with self.engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            DO $patch$
                            BEGIN
                              IF EXISTS (
                                SELECT 1 FROM information_schema.tables
                                WHERE table_schema = 'routing' AND table_name = 'route_candidates'
                              ) THEN
                                ALTER TABLE routing.route_candidates
                                  ADD COLUMN IF NOT EXISTS area_road_sequence JSONB;
                              END IF;
                            END
                            $patch$;
                            """
                        )
                    )

            # create_all 不會為既有表補新欄位：permit.* 增量欄位以 IF NOT EXISTS 補齊
            if self.engine.dialect.name == "postgresql":
                with self.engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            DO $permit_patch$
                            BEGIN
                              IF EXISTS (
                                SELECT 1 FROM information_schema.tables
                                WHERE table_schema = 'permit' AND table_name = 'permits'
                              ) THEN
                                ALTER TABLE permit.permits
                                  ADD COLUMN IF NOT EXISTS issued_by UUID;
                                ALTER TABLE permit.permits
                                  ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ;
                                ALTER TABLE permit.permits
                                  ADD COLUMN IF NOT EXISTS revoked_by UUID;
                                ALTER TABLE permit.permits
                                  ADD COLUMN IF NOT EXISTS revoked_reason TEXT;
                              END IF;
                              IF EXISTS (
                                SELECT 1 FROM information_schema.tables
                                WHERE table_schema = 'permit' AND table_name = 'documents'
                              ) THEN
                                ALTER TABLE permit.documents
                                  ADD COLUMN IF NOT EXISTS is_latest BOOLEAN NOT NULL DEFAULT TRUE;
                                ALTER TABLE permit.documents
                                  ADD COLUMN IF NOT EXISTS checksum_sha256 VARCHAR(64);
                                ALTER TABLE permit.documents
                                  ADD COLUMN IF NOT EXISTS error_message TEXT;
                                ALTER TABLE permit.documents
                                  ADD COLUMN IF NOT EXISTS generated_at TIMESTAMPTZ;
                              END IF;
                              IF EXISTS (
                                SELECT 1 FROM information_schema.tables
                                WHERE table_schema = 'permit' AND table_name = 'document_jobs'
                              ) THEN
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS triggered_by UUID;
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS trigger_source VARCHAR(30) NOT NULL DEFAULT 'system';
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS payload_json JSONB;
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ;
                                ALTER TABLE permit.document_jobs
                                  ADD COLUMN IF NOT EXISTS finished_at TIMESTAMPTZ;
                              END IF;
                            END
                            $permit_patch$;
                            """
                        )
                    )

            # create_all 不會為既有表補新欄位：review.supplement_requests.title
            if self.engine.dialect.name == "postgresql":
                with self.engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            DO $review_supplement_patch$
                            BEGIN
                              IF EXISTS (
                                SELECT 1 FROM information_schema.tables
                                WHERE table_schema = 'review' AND table_name = 'supplement_requests'
                              ) THEN
                                ALTER TABLE review.supplement_requests
                                  ADD COLUMN IF NOT EXISTS title VARCHAR(200) NOT NULL DEFAULT '';
                                ALTER TABLE review.supplement_requests
                                  ADD COLUMN IF NOT EXISTS applicant_response_note TEXT;
                                ALTER TABLE review.supplement_requests
                                  ADD COLUMN IF NOT EXISTS responded_at TIMESTAMPTZ;
                              END IF;
                            END
                            $review_supplement_patch$;
                            """
                        )
                    )

            logger.db_info("All tables created successfully")
            
        except Exception as e:
            logger.db_error(f"Failed to create tables - {str(e)}")
            raise
    
    def _scan_schema_modules(self) -> List[str]:
        """
        掃描所有 context 的 schema 模組
        
        Returns:
            schema 模組路徑列表
        """
        schema_modules = []
        
        if not self.contexts_path.exists():
            logger.db_info("Contexts directory not found")
            return schema_modules
        
        # 掃描所有 context 目錄
        for context_dir in self.contexts_path.iterdir():
            if context_dir.is_dir():
                schema_dir = context_dir / "infra" / "schema"
                if schema_dir.exists():
                    # 掃描 schema 目錄中的 Python 檔案
                    for schema_file in schema_dir.glob("*.py"):
                        if schema_file.name != "__init__.py":
                            module_name = f"src.contexts.{context_dir.name}.infra.schema.{schema_file.stem}"
                            schema_modules.append(module_name)
        
        logger.db_info(f"Found {len(schema_modules)} schema modules")
        return schema_modules
    
    def _import_schema_module(self, module_path: str):
        """
        匯入 schema 模組
        
        Args:
            module_path: 模組路徑
        """
        try:
            importlib.import_module(module_path)
            context_name = module_path.split('.')[2]  # 提取 context 名稱
            logger.db_info(f"Schema module imported: {module_path} (context={context_name})")
        except Exception as e:
            logger.db_error(f"Failed to import schema module {module_path} - {str(e)}")
            raise
    
    def _import_seed_data(self):
        """匯入 seed 資料"""
        try:
            # 掃描所有 context 的 seed 資料目錄
            seed_directories = self._scan_seed_data_directories()
            
            if not seed_directories:
                logger.db_info("No seed data directories found")
                return
            
            # 匯入所有 seed 資料
            for seed_info in seed_directories:
                if (
                    seed_info["context"] == "routing_restriction"
                    and not self._postgis_available
                ):
                    logger.db_info(
                        "略過 routing_restriction seed（PostGIS 不可用、routing 資料表未建立）"
                    )
                    continue
                self._import_seed_data_from_directory(seed_info)
            
            logger.db_info("All seed data imported successfully")
            
        except Exception as e:
            logger.db_error(f"Failed to import seed data - {str(e)}")
            raise
    
    def _scan_seed_data_directories(self) -> List[Dict[str, str]]:
        """
        直接掃描所有 context 的 seed 資料目錄
        
        Returns:
            List[Dict[str, str]]: seed 資料目錄資訊列表
        """
        seed_directories = []
        
        if not self.contexts_path.exists():
            return seed_directories
        
        # 掃描所有 context 目錄
        for context_dir in self.contexts_path.iterdir():
            if context_dir.is_dir():
                seed_data_dir = context_dir / "infra" / "seed" / "data"
                if seed_data_dir.exists():
                    # 掃描 data 目錄中的 JSON 檔案
                    json_files = list(seed_data_dir.glob("*.json"))
                    if json_files:
                        seed_directories.append({
                            "context": context_dir.name,
                            "seed_dir": str(seed_data_dir),
                            "json_files": [f.stem for f in json_files]
                        })
        
        logger.db_info(f"Found {len(seed_directories)} seed data directories")
        return seed_directories
    
    def _import_seed_data_from_directory(self, seed_info: Dict[str, str]):
        """
        從目錄匯入 seed 資料
        
        Args:
            seed_info: seed 目錄資訊
        """
        try:
            from shared.utils.seed_loader import load_seed_data
            from shared.core.db.connection import get_session
            
            context_name = seed_info["context"]
            seed_dir = seed_info["seed_dir"]
            json_files = seed_info["json_files"]
            # 固定載入順序，避免外鍵依賴表因檔名排序／glob 順序導致 seed 失敗
            _CONTEXT_SEED_ORDER: Dict[str, tuple[str, ...]] = {
                "application": (
                    "applications",
                    "stored_files",
                    "applicant_profiles",
                    "company_profiles",
                    "vehicles",
                    "checklists",
                    "status_histories",
                    "attachments",
                ),
                "routing_restriction": (
                    "map_layers",
                    "restriction_rules",
                    "rule_geometries",
                    "rule_time_windows",
                    "route_requests",
                    "route_plans",
                    "route_candidates",
                    "route_segments",
                    "route_rule_hits",
                    "officer_route_overrides",
                ),
                "review_decision": (
                    "review_tasks",
                    "supplement_requests",
                    "supplement_items",
                    "decisions",
                    "review_comments",
                ),
                "permit_document": (
                    "permits",
                    "documents",
                    "document_jobs",
                ),
                "page_model_query_aggregation": (
                    "page_model_snapshots",
                ),
                "iam": (
                    "roles",
                    "permissions",
                    "role_permissions",
                    "users",
                    "role_assignments",
                    "sessions",
                    "mfa_challenges",
                ),
            }
            _seed_table_order = _CONTEXT_SEED_ORDER.get(
                context_name,
                tuple(),
            )

            def _seed_order_key(name: str) -> tuple[int, str]:
                try:
                    return (_seed_table_order.index(name), name)
                except ValueError:
                    return (len(_seed_table_order), name)

            ordered_tables = sorted(json_files, key=_seed_order_key)

            logger.db_info(f"Processing seed data for context: {context_name}")
            
            with get_session() as session:
                for table_name in ordered_tables:
                    try:
                        # 載入 seed 資料
                        seed_data = load_seed_data(table_name, seed_dir)
                        if not seed_data:
                            logger.db_info(f"No seed data found for {table_name}")
                            continue
                        
                        # 獲取對應的 Schema 類別
                        schema_class = self._get_schema_class_by_table_name(table_name, context_name)
                        if not schema_class:
                            logger.db_info(f"No schema class found for table: {table_name}")
                            continue
                        
                        # 檢查現有資料
                        try:
                            existing_count = session.query(schema_class).count()
                            if existing_count > 0:
                                logger.db_info(f"Seed skipped for {table_name} - {existing_count} records already exist")
                                continue
                        except Exception:
                            # 表不存在時，count() 已讓此 session 的交易進入 aborted；必須先 rollback
                            # 才能繼續在同一 session 內 INSERT，否則會出現 InFailedSqlTransaction。
                            session.rollback()
                            logger.db_info(f"Table for {table_name} does not exist, creating...")
                            schema_class.metadata.create_all(bind=self.engine)
                            logger.db_info(f"Table for {table_name} created successfully")
                        
                        # 轉換為 Schema 物件並插入
                        schema_objects = []
                        for data in seed_data:
                            # 如果 JSON 中沒有 id 欄位，移除它讓資料庫自動生成
                            if 'id' in data and data['id'] is None:
                                data = {k: v for k, v in data.items() if k != 'id'}
                            schema_obj = schema_class(**data)
                            schema_objects.append(schema_obj)
                        
                        # 批量插入
                        session.add_all(schema_objects)
                        session.commit()
                        
                        logger.db_info(f"Seed data imported for {table_name} - {len(schema_objects)} records created")
                        
                    except Exception as e:
                        session.rollback()
                        logger.db_error(f"Failed to import seed data for {table_name}: {str(e)}")
                        raise
                        
        except Exception as e:
            logger.db_error(f"Failed to process seed data for context {context_name}: {str(e)}")
            raise
    
    def _get_schema_class_by_table_name(self, table_name: str, context_name: str):
        """
        根據表名和 context 名稱獲取 Schema 類別
        
        Args:
            table_name: 表名
            context_name: context 名稱
            
        Returns:
            Schema 類別或 None
        """
        try:
            # 動態導入 context 的 schema 模組
            schema_module_path = f"src.contexts.{context_name}.infra.schema"
            schema_module = importlib.import_module(schema_module_path)
            
            # 特殊表名 → ORM 類別映射（無映射時依表名轉 PascalCase）。
            table_to_class_mapping: Dict[str, str] = {}

            class_name = table_to_class_mapping.get(table_name)
            
            # 如果沒有找到映射，嘗試直接使用表名作為類別名
            if not class_name:
                class_name = table_name.title().replace("_", "")
            
            if class_name and hasattr(schema_module, class_name):
                return getattr(schema_module, class_name)
            
            logger.db_info(f"No mapping found for table: {table_name}")
            return None
            
        except Exception as e:
            logger.db_error(f"Failed to get schema class for {table_name}: {str(e)}")
            return None
    
    def _import_seed_module(self, module_path: str):
        """
        匯入 seed 模組
        
        Args:
            module_path: 模組路徑
        """
        try:
            module = importlib.import_module(module_path)
            context_name = module_path.split('.')[2]  # 提取 context 名稱
            
            # 檢查模組是否有 get_user_seed_provider 函數（新的統一接口）
            if hasattr(module, 'get_user_seed_provider'):
                self._process_seed_provider(module.get_user_seed_provider(), context_name)
            elif hasattr(module, 'run_seed'):
                # 向後兼容舊的 run_seed 函數
                module.run_seed()
                logger.db_info(f"Seed data imported (context={context_name}) - using legacy run_seed")
            else:
                logger.db_info(f"Seed module {module_path} has no seed provider function, skipping")
                
        except Exception as e:
            logger.db_error(f"Failed to import seed module {module_path} - {str(e)}")
            raise
    
    def _process_seed_provider(self, seed_provider, context_name: str):
        """
        處理 seed 資料提供器
        
        Args:
            seed_provider: seed 資料提供器
            context_name: context 名稱
        """
        try:
            from shared.core.db.connection import get_session
            
            # 獲取 seed 資訊
            seed_info = seed_provider.get_seed_info()
            logger.db_info(f"Processing seed for context={context_name}: {seed_info}")
            
            # 驗證 seed 資料
            if not seed_provider.validate_seed_data():
                logger.db_error(f"Seed data validation failed for context={context_name}")
                return
            
            with get_session() as session:
                # 獲取 Schema 類別
                schema_class = seed_provider.get_schema_class()
                
                # 檢查現有資料
                try:
                    existing_count = session.query(schema_class).count()
                    if existing_count > 0:
                        logger.db_info(f"Seed skipped for {context_name} - {existing_count} records already exist")
                        return
                except Exception:
                    # 表不存在，先創建表
                    logger.db_info(f"Table for {context_name} does not exist, creating...")
                    schema_class.metadata.create_all(bind=self.engine)
                    logger.db_info(f"Table for {context_name} created successfully")
                
                # 獲取 seed 資料
                seed_data = seed_provider.get_seed_data()
                if not seed_data:
                    logger.db_info(f"No seed data found for {context_name}")
                    return
                
                # 轉換為 Schema 物件
                schema_objects = seed_provider.convert_to_schema_objects(seed_data)
                
                # 批量插入
                session.add_all(schema_objects)
                session.commit()
                
                logger.db_info(f"Seed data imported for {context_name} - {len(schema_objects)} records created")
                
        except Exception as e:
            logger.db_error(f"Failed to process seed provider for {context_name} - {str(e)}")
            raise


def init_db() -> bool:
    """
    初始化資料庫
    
    Returns:
        是否初始化成功
    """
    initializer = DatabaseInitializer()
    return initializer.init_database()
