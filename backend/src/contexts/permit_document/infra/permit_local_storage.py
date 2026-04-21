"""
本機許可證 PDF 路徑與簽名下載 URL（無 S3／GCS 時）。

責任：UC-PERMIT-02 產出之 PDF 寫入磁碟；UC-PERMIT-03 回傳可於瀏覽器開啟之
``/api/v1/stored-files/{file_id}/download?expires=&sig=`` 連結（HMAC 短期有效）。
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from shared.core.config import settings


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[4]


def permit_certificate_files_directory() -> Path:
    if settings.permit_certificate_files_dir:
        return Path(settings.permit_certificate_files_dir)
    return _backend_root() / ".local_permit_files"


def permit_certificate_pdf_path(file_id: UUID) -> Path:
    return permit_certificate_files_directory() / f"{file_id}.pdf"


def public_api_origin() -> str:
    base = settings.public_api_base_url
    if base:
        return base.rstrip("/")
    api = settings.api
    host = api.host
    if host in ("0.0.0.0", "::"):
        host = "127.0.0.1"
    return f"http://{host}:{api.port}"


def sign_download(file_id: UUID, expires_unix: int) -> str:
    secret = settings.security.jwt_secret
    msg = f"{file_id}:{expires_unix}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def verify_download(file_id: UUID, expires_unix: int, sig: str) -> bool:
    try:
        sig_norm = sig.strip().lower()
        if len(sig_norm) != 64:
            return False
        expected = sign_download(file_id, expires_unix)
        return hmac.compare_digest(expected, sig_norm)
    except Exception:
        return False


def build_temporary_download_url(
    *,
    file_id: UUID,
    ttl_seconds: int = 600,
) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    exp_unix = int(expires.timestamp())
    sig = sign_download(file_id, exp_unix)
    origin = public_api_origin()
    url = f"{origin}/api/v1/stored-files/{file_id}/download?expires={exp_unix}&sig={sig}"
    return url, expires
