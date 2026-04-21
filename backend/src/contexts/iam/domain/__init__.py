"""
IAM bounded context — domain layer only (identity & access management).

此套件對應規格 4.1 之 Aggregate／Value Object 與核心規則（身分與存取 IAM）；
不包含 Infra／App／API。說明：若文件標題誤寫為 Backtest，語意上仍指本 IAM context。
"""

from . import entities, errors, ports, value_objects

__all__ = ["entities", "errors", "ports", "value_objects"]
