"""
run_tests.py — 舊版曾執行 user context 單元測試；該 context 已移除，改指向 IAM 單元測試。

請以專案根目錄執行：python -m pytest shared/tests/unit/contexts/iam -q
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_tests() -> bool:
    root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(root / "shared/tests/unit/contexts/iam"),
        "-q",
        "--tb=short",
    ]
    print("=== IAM 單元測試（取代已移除之 user context）===")
    r = subprocess.run(cmd, cwd=str(root), env=env)
    return r.returncode == 0


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
