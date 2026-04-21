#!/usr/bin/env python3
"""
Verify PostgreSQL connectivity using the same settings as the app (.env).
Run from repository root: python scripts/check_postgres_connection.py
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

    os.chdir(root)

    try:
        from sqlalchemy import create_engine, text

        from shared.core.config import settings
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        return 1

    url = settings.database.database_url
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            one = conn.execute(text("SELECT 1")).scalar_one()
            dbname = conn.execute(text("SELECT current_database()")).scalar_one()
        engine.dispose()
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}", file=sys.stderr)
        return 1

    if one != 1:
        print("Unexpected SELECT 1 result", file=sys.stderr)
        return 1

    print(f"OK: connected to PostgreSQL database={dbname!r} host={settings.database.host!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
