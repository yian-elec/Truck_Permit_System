#!/usr/bin/env python3
"""
UC-PERMIT-02 worker：輪詢 `permit.document_jobs` 之 pending 工作並產製使用證 PDF。

前置：PostgreSQL 已建表、`PYTHONPATH` 指到 `backend`（與專案慣例一致）。

範例::

  cd backend && python scripts/run_permit_certificate_jobs.py --once
  cd backend && python scripts/run_permit_certificate_jobs.py --limit 10
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# 專案根：backend/
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.contexts.permit_document.app.services.certificate_generation_application_service import (  # noqa: E402
    CertificateGenerationApplicationService,
)
from src.contexts.permit_document.app.services.permit_service_context import PermitServiceContext  # noqa: E402
from src.contexts.permit_document.app.services.ports.default_adapters import (  # noqa: E402
    build_default_permit_service_context_dependencies,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Permit certificate PDF generation worker")
    p.add_argument("--once", action="store_true", help="處理佇列直到空或達到 --limit")
    p.add_argument("--limit", type=int, default=1, help="最多處理幾筆 pending job（預設 1）")
    p.add_argument("--sleep", type=float, default=2.0, help="輪詢間隔秒數（未使用 --once 時）")
    args = p.parse_args()

    auth, storage = build_default_permit_service_context_dependencies()
    ctx = PermitServiceContext(authorization=auth, object_storage=storage)
    svc = CertificateGenerationApplicationService(ctx)

    processed = 0
    if args.once:
        while processed < args.limit:
            r = svc.process_next_pending_job()
            if r == "empty":
                break
            processed += 1
            if r == "error":
                continue
        print(f"done: processed_attempts={processed}")
        return

    while True:
        r = svc.process_next_pending_job()
        if r == "empty":
            time.sleep(args.sleep)
            continue
        print(r)


if __name__ == "__main__":
    main()
