"""
與 cwd 無關的 backend/.env 路徑。

巢狀 *Config 若使用相對路徑 '.env'，從 repo 根目錄啟動時會讀不到 backend/.env，
導致 GEOCODING_MODE、DB_* 等全部退回預設值。
"""

from __future__ import annotations

from pathlib import Path

# 本檔位於 shared/core/config/，上兩層為 backend/
_BACKEND_DIR = Path(__file__).resolve().parent.parents[2]
_BACKEND_DOTENV = _BACKEND_DIR / ".env"


def backend_env_file() -> str:
    """供 pydantic Settings 的 env_file；優先使用 backend/.env。"""
    return str(_BACKEND_DOTENV) if _BACKEND_DOTENV.is_file() else ".env"
