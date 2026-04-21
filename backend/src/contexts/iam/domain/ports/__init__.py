"""
IAM 領域連接埠（Protocol）

對應規格 4.2「外部資源」之抽象邊界：僅定義介面，實作屬 Infra／Adapter。
Domain 不依賴具體技術，App 層注入實作並協調用例。
"""

from .policy_ports import AuthProviderPort, MfaSenderPort, TokenIssuerPort

__all__ = ["AuthProviderPort", "MfaSenderPort", "TokenIssuerPort"]
