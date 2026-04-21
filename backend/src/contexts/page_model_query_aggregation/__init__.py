"""
Page_Model_Query_Aggregation bounded context。

責任：定義「畫面專用 Page Model」之領域模型與組版規則（read model 聚合），
供 App 層呼叫下游 context 並組裝 DTO 時遵循同一套不變條件與區塊契約。

已包含 `domain`、`app`、`infra`、`api`；於 `main.py` 註冊三組 Page Model 路由。
"""
