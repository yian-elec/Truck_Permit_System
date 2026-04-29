"""
settings.py - 主設定檔
集中管理所有設定，統一入口
"""

from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from .db_config import DatabaseConfig
from .env_file_path import backend_env_file
from .security_config import SecurityConfig
from .api_config import APIConfig
from .test_config import TestConfig
from .seed_config import SeedConfig
from .ai_config import AIConfig

GeocodingMode = Literal["stub", "nominatim"]


class Settings(BaseSettings):
    """
    主設定類別
    集中管理所有設定，統一入口
    """
    
    # 環境設定
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # 資料庫設定
    database: DatabaseConfig = DatabaseConfig()
    
    # 安全設定
    security: SecurityConfig = SecurityConfig()
    
    # API 設定
    api: APIConfig = APIConfig()
    
    # 測試設定
    test: TestConfig = TestConfig()
    
    # Seed 設定
    seed: SeedConfig = SeedConfig()
    
    # AI 設定
    ai: AIConfig = AIConfig()
    
    # 日誌設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # 其他設定
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    external_api_key: Optional[str] = Field(default=None, env="EXTERNAL_API_KEY")

    # UC-ROUTE-01：地理編碼（stub=雜湊假座標；nominatim=OSM Nominatim，須設定 NOMINATIM_USER_AGENT）
    geocoding_mode: GeocodingMode = Field(default="stub", env="GEOCODING_MODE")
    nominatim_base_url: str = Field(
        default="https://nominatim.openstreetmap.org",
        env="NOMINATIM_BASE_URL",
    )
    nominatim_timeout_s: float = Field(default=10.0, env="NOMINATIM_TIMEOUT_S")
    nominatim_user_agent: Optional[str] = Field(default=None, env="NOMINATIM_USER_AGENT")

    # UC-ROUTE-02：候選路線 provider（original=Stub；mvp=Overpass 道路鏈）
    routing_mode: Literal["original", "mvp"] = Field(default="original", env="ROUTING_MODE")
    overpass_url: str = Field(
        default="https://overpass-api.de/api/interpreter",
        env="OVERPASS_URL",
    )
    overpass_timeout_s: float = Field(default=60.0, env="OVERPASS_TIMEOUT_S")
    # overpass-api.de 要求可識別之 User-Agent（非瀏覽器預設/httpx 預設可導致 HTTP 406）；上線請改為含聯絡資訊之字串
    overpass_user_agent: str = Field(
        default="TruckPermitRouting/1.0 (heavy truck permit; MVP route planning)",
        env="OVERPASS_USER_AGENT",
    )

    # 道路資料層：Overpass bbox 緩衝（度）、query 簽章版本、路名 fallback
    road_fetch_bbox_pad_deg: float = Field(default=0.02, env="ROAD_FETCH_BBOX_PAD_DEG")
    overpass_query_version: str = Field(default="1", env="OVERPASS_QUERY_VERSION")
    osm_road_name_fallback: str = Field(default="未命名道路", env="OSM_ROAD_NAME_FALLBACK")

    # MVP：選路前依 forbidden 幾何排除整條 way；若全批都被排除則子圖為空。預設在「全無 way」時回退為未篩選圖，
    # 仍由 attach_rule_hits 驗證；設為 false 可強制維持嚴格排除（可能無候選）。
    mvp_routing_apply_forbidden_prefilter: bool = Field(
        default=True,
        env="MVP_ROUTING_APPLY_FORBIDDEN_PREFILTER",
    )
    mvp_routing_fallback_unfiltered_when_all_blocked: bool = Field(
        default=True,
        env="MVP_ROUTING_FALLBACK_UNFILTERED_WHEN_ALL_BLOCKED",
    )
    # MVP 組圖：若為 true，僅納入 OSM 上同時具備非空 name 或 ref 的 way（與路名規則一致）。
    # 設為 true 時，起訖若僅能經無名路段連通，會無候選；需「可走無名但加罰」時須設為 false，
    # 否則無名 way 不會進圖，readability 懲罰不會生效。
    mvp_routing_require_way_name_or_ref: bool = Field(
        default=False,
        env="MVP_ROUTING_REQUIRE_WAY_NAME_OR_REF",
    )
    # MVP 邊成本：無 name/ref 時將距離×highway 再乘以此係數（與 way_has_osm_name_or_ref 對齊）。
    mvp_routing_readability_unnamed_multiplier: float = Field(
        default=1.75,
        env="MVP_ROUTING_READABILITY_UNNAMED_MULTIPLIER",
    )

    # UC-PERMIT：本機 PDF 目錄（預設 {backend}/.local_permit_files）；上線換雲端儲存時可廢止
    permit_certificate_files_dir: Optional[str] = Field(default=None, env="PERMIT_CERTIFICATE_FILES_DIR")
    # 簽名下載連結之公開原點（前端／瀏覽器可達）；未設時以 API 埠推算，0.0.0.0 改為 127.0.0.1
    public_api_base_url: Optional[str] = Field(default=None, env="PUBLIC_API_BASE_URL")

    class Config:
        # 固定讀取 backend/.env，避免從 repo 根目錄或其他 cwd 啟動 uvicorn 時讀不到
        # GEOCODING_MODE 等變數而默默退回預設 stub。
        env_file = backend_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# 全域設定實例
settings = Settings()
