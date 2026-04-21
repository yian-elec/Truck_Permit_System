# 使用範例目錄

本目錄包含各種功能的使用範例。

## 📂 範例列表

### AI Service 範例
- **ai_service_example.py** - AI Service 完整使用範例
  - 基礎對話
  - 系統提示詞
  - 預設模板
  - 多輪對話
  - 串流輸出
  - 文字摘要
  - 翻譯功能
  - 程式碼生成
  - JSON 提取

## 🚀 如何運行範例

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
```bash
# 複製環境變數範例
cp docs/env.example .env

# 編輯 .env 文件，設定你的 OpenAI API Key
# OPENAI_API_KEY=your-api-key-here
```

### 3. 運行範例
```bash
# AI Service 範例
python examples/ai_service_example.py
```

## 💡 提示

- 確保已經設定 `OPENAI_API_KEY` 環境變數
- 某些範例需要網路連接
- 注意 API 使用配額和成本

## 📚 更多資訊

查看各服務的 README 文件以獲取更詳細的文檔：
- [AI Service README](../src/shared/services/ai/README.md)

