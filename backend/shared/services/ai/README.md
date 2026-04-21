# AI Service 使用文檔

基於 LangChain 和 OpenAI 的 AI 服務模組，提供簡單易用的 AI 對話功能。

## 🚀 快速開始

### 1. 環境配置

在 `.env` 文件中添加 OpenAI API Key：

```env
OPENAI_API_KEY=your-openai-api-key-here
AI_DEFAULT_MODEL=gpt-3.5-turbo
AI_DEFAULT_TEMPERATURE=0.7
```

### 2. 基礎使用

```python
from src.shared.services.ai import ai_service

# 簡單對話
response = await ai_service.chat(
    message="你好，請介紹一下自己",
    model="gpt-3.5-turbo"
)
print(response.message)
```

## 📚 功能特性

### 1. 基礎對話

發送訊息並獲得 AI 回應：

```python
response = await ai_service.chat(
    message="什麼是 Python？",
    model="gpt-4",  # 可選，預設使用配置中的模型
    system_prompt="你是一個專業的程式設計師",  # 可選
    temperature=0.7,  # 可選，控制回應的隨機性
    max_tokens=500  # 可選，限制回應長度
)

print(f"AI: {response.message}")
print(f"使用模型: {response.model}")
print(f"使用 tokens: {response.tokens_used}")
```

### 2. 使用預設模板

使用內建的專業提示詞模板：

```python
# 程式設計助手
response = await ai_service.chat_with_template(
    message="請幫我寫一個 Python 快速排序函數",
    template_name="programming",
    model="gpt-4"
)

# 翻譯助手
response = await ai_service.chat_with_template(
    message="Hello, how are you?",
    template_name="translation"
)

# 可用的模板：
# - general: 通用助手
# - programming: 程式設計助手
# - translation: 翻譯助手
# - writing: 寫作助手
# - data_analyst: 資料分析助手
# - customer_service: 客服助手
# - teaching: 教學助手
# - json: JSON 生成助手
# - summarizer: 摘要助手
# - sql: SQL 助手
```

### 3. 對話歷史管理

維護多輪對話的上下文：

```python
# 創建新對話
conversation_id = ai_service.create_conversation()

# 發送第一條訊息
response1 = await ai_service.chat(
    message="我想學習 Python",
    conversation_id=conversation_id
)

# 發送後續訊息（AI 會記住之前的對話）
response2 = await ai_service.chat(
    message="從哪裡開始比較好？",
    conversation_id=conversation_id
)

# 取得對話歷史
history = ai_service.get_conversation(conversation_id)
for msg in history.messages:
    print(f"{msg.role}: {msg.content}")

# 清除對話歷史
ai_service.clear_conversation(conversation_id)

# 刪除對話
ai_service.delete_conversation(conversation_id)
```

### 4. 串流輸出

實時獲得 AI 回應（適用於長回應）：

```python
async for chunk in ai_service.stream_chat(
    message="請寫一篇關於人工智慧的文章",
    model="gpt-4",
    system_prompt="你是一個專業作家"
):
    if not chunk.is_final:
        print(chunk.content, end="", flush=True)
    else:
        print("\n[完成]")
```

### 5. 文字摘要

快速生成文字摘要：

```python
long_text = """
這裡是一段很長的文字...
"""

summary = await ai_service.summarize_text(
    text=long_text,
    max_length=200,  # 最大摘要長度
    model="gpt-3.5-turbo"
)
print(f"摘要: {summary}")
```

### 6. 文字翻譯

智能翻譯功能：

```python
# 基礎翻譯
translation = await ai_service.translate_text(
    text="Hello, how are you?",
    target_language="繁體中文"
)

# 指定來源語言
translation = await ai_service.translate_text(
    text="Bonjour",
    source_language="法文",
    target_language="英文"
)
```

### 7. 程式碼生成

自動生成程式碼：

```python
code = await ai_service.generate_code(
    description="實現一個二分搜尋算法",
    language="Python",
    model="gpt-4"
)
print(code)
```

### 8. JSON 提取

從文字中提取結構化資料：

```python
text = "張三，30 歲，住在台北市，職業是工程師"

json_data = await ai_service.extract_json(
    text=text,
    schema_description="""
    {
        "name": "姓名",
        "age": "年齡（數字）",
        "city": "城市",
        "occupation": "職業"
    }
    """
)
print(json_data)  # 返回 JSON 字串
```

### 9. 查詢可用資源

```python
# 取得可用的 AI 模型
models = ai_service.get_available_models()
print(f"可用模型: {models}")

# 取得可用的提示詞模板
templates = ai_service.get_available_templates()
for name, prompt in templates.items():
    print(f"{name}: {prompt[:50]}...")
```

## 🔧 高級配置

### 自定義配置

在 `.env` 中調整配置：

```env
# 預設模型
AI_DEFAULT_MODEL=gpt-4

# 溫度參數（0-2，越高越隨機）
AI_DEFAULT_TEMPERATURE=0.7

# 最大 token 數
AI_DEFAULT_MAX_TOKENS=2000

# 請求超時時間（秒）
AI_REQUEST_TIMEOUT=120

# 最大重試次數
AI_MAX_RETRIES=3

# 對話歷史最大訊息數
AI_MAX_HISTORY_MESSAGES=20
```

## 📊 模型選擇建議

### GPT-4 系列
- **gpt-4**: 最強大，適合複雜任務
- **gpt-4-turbo-preview**: 更快速的 GPT-4
- **gpt-4-1106-preview**: 最新版 GPT-4

### GPT-3.5 系列
- **gpt-3.5-turbo**: 經濟實惠，速度快
- **gpt-3.5-turbo-16k**: 支持更長的上下文

### 選擇建議
- 簡單對話、翻譯：gpt-3.5-turbo
- 程式碼生成、複雜推理：gpt-4
- 長文本處理：gpt-3.5-turbo-16k 或 gpt-4

## 🎯 最佳實踐

### 1. 溫度參數設定
```python
# 創意寫作、腦力激盪
temperature=0.9

# 一般對話
temperature=0.7

# 程式碼生成、資料提取
temperature=0.2
```

### 2. 錯誤處理
```python
try:
    response = await ai_service.chat(message="你好")
except Exception as e:
    logger.error(f"AI 請求失敗: {str(e)}")
    # 處理錯誤
```

### 3. 成本控制
```python
# 使用較便宜的模型
response = await ai_service.chat(
    message="簡單問題",
    model="gpt-3.5-turbo"
)

# 限制回應長度
response = await ai_service.chat(
    message="請簡短回答",
    max_tokens=100
)
```

## 📝 完整範例

請查看 `examples/ai_service_example.py` 獲取更多完整範例。

## ⚠️ 注意事項

1. **API Key 安全**: 不要將 API Key 提交到版本控制系統
2. **成本控制**: GPT-4 比 GPT-3.5 貴很多，注意使用量
3. **速率限制**: OpenAI 有 API 速率限制，請適當處理
4. **資料隱私**: 不要發送敏感資料到 OpenAI
5. **錯誤重試**: 服務已內建重試機制，但請妥善處理異常

## 🔗 相關資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [LangChain 文檔](https://python.langchain.com/)
- [定價資訊](https://openai.com/pricing)

