"""
Application context — Infrastructure 層。

責任：ORM schema、seed 資料、Repository 實作；資料庫存取一律透過 `shared.core.db` 之 `get_session`／`BaseRepository` 模式。
"""
