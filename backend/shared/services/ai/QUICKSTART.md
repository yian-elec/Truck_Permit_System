# AI Service 快速開始

5 分鐘快速開始使用 AI Service！

## 🚀 快速設定（3 步驟）

### 步驟 1: 安裝依賴

```bash
pip install -r requirements.txt
```

### 步驟 2: 設定 API Key

在專案根目錄創建 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

> 💡 在 [OpenAI Platform](https://platform.openai.com/api-keys) 取得你的 API Key

### 步驟 3: 測試服務

```bash
python examples/quick_test_ai.py
```

如果看到 "✅ AI Service 測試成功！"，表示設定完成！

## 📝 5 分鐘上手

### 1. 最簡單的使用

```python
from src.shared.services.ai import ai_service

# 發送訊息
response = await ai_service.chat(message="你好，請介紹一下自己")
print(response.message)
```

### 2. 選擇不同的模型

```python
# 使用 GPT-4（更強大但更貴）
response = await ai_service.chat(
    message="解釋量子計算",
    model="gpt-4"
)

# 使用 GPT-3.5（快速且經濟）
response = await ai_service.chat(
    message="今天天氣如何？",
    model="gpt-3.5-turbo"
)
```

### 3. 使用預設角色模板

```python
# 程式設計助手
response = await ai_service.chat_with_template(
    message="寫一個排序算法",
    template_name="programming"
)

# 翻譯助手
response = await ai_service.chat_with_template(
    message="Hello, how are you?",
    template_name="translation"
)
```

### 4. 維護對話歷史

```python
# 創建對話
conversation_id = ai_service.create_conversation()

# 多輪對話
response1 = await ai_service.chat(
    message="我想學 Python",
    conversation_id=conversation_id
)

response2 = await ai_service.chat(
    message="從哪裡開始？",  # AI 會記住前面的對話
    conversation_id=conversation_id
)
```

### 5. 實用工具函數

```python
# 文字摘要
summary = await ai_service.summarize_text(
    text="很長的文章...",
    max_length=100
)

# 翻譯
translation = await ai_service.translate_text(
    text="Hello World",
    target_language="繁體中文"
)

# 生成程式碼
code = await ai_service.generate_code(
    description="實現快速排序",
    language="Python"
)
```

## 🎯 常用範例

### 範例 1: 客服機器人

```python
conversation_id = ai_service.create_conversation()

while True:
    user_input = input("用戶: ")
    if user_input.lower() in ['quit', 'exit']:
        break
    
    response = await ai_service.chat(
        message=user_input,
        conversation_id=conversation_id,
        system_prompt="你是一個專業且友善的客服人員"
    )
    
    print(f"客服: {response.message}")
```

### 範例 2: 程式碼審查助手

```python
code_to_review = """
def calculate(x, y):
    return x/y
"""

response = await ai_service.chat(
    message=f"請審查這段程式碼並提供改進建議：\n{code_to_review}",
    model="gpt-4",
    system_prompt=PromptTemplates.PROGRAMMING_ASSISTANT
)

print(response.message)
```

### 範例 3: 批量文字處理

```python
texts = ["文字1", "文字2", "文字3"]
summaries = []

for text in texts:
    summary = await ai_service.summarize_text(text, max_length=50)
    summaries.append(summary)
```

## 💡 實用技巧

### 控制回應風格

```python
# 創意寫作（更隨機）
response = await ai_service.chat(
    message="寫一首詩",
    temperature=0.9  # 0-2，越高越有創意
)

# 精確回答（更確定）
response = await ai_service.chat(
    message="2+2等於多少？",
    temperature=0.1  # 更確定的答案
)
```

### 限制回應長度

```python
response = await ai_service.chat(
    message="介紹 Python",
    max_tokens=100  # 限制在 100 tokens
)
```

### 串流輸出（即時顯示）

```python
async for chunk in ai_service.stream_chat(message="寫一篇文章"):
    if not chunk.is_final:
        print(chunk.content, end="", flush=True)
```

## ⚙️ 配置調整

在 `.env` 文件中調整設定：

```env
# 預設模型
AI_DEFAULT_MODEL=gpt-4

# 預設溫度（創意程度）
AI_DEFAULT_TEMPERATURE=0.7

# 最大 token 數
AI_DEFAULT_MAX_TOKENS=2000

# 對話歷史保留訊息數
AI_MAX_HISTORY_MESSAGES=20
```

## 📊 模型選擇指南

| 模型 | 速度 | 成本 | 適合場景 |
|------|------|------|----------|
| gpt-3.5-turbo | ⚡⚡⚡ | 💰 | 一般對話、簡單任務 |
| gpt-3.5-turbo-16k | ⚡⚡ | 💰💰 | 長文本處理 |
| gpt-4 | ⚡ | 💰💰💰 | 複雜推理、程式碼生成 |
| gpt-4-turbo | ⚡⚡ | 💰💰 | GPT-4 的快速版本 |

## ❓ 常見問題

**Q: 為什麼出現 API Key 錯誤？**  
A: 確認 `.env` 文件中的 `OPENAI_API_KEY` 設定正確

**Q: 如何降低成本？**  
A: 使用 `gpt-3.5-turbo` 並設定 `max_tokens` 限制

**Q: 如何處理速率限制？**  
A: 服務已內建重試機制，也可以調整 `AI_MAX_RETRIES`

**Q: 串流輸出如何使用？**  
A: 查看 `examples/ai_service_example.py` 中的 `example_streaming()`

## 📚 更多資源

- [完整文檔](./README.md)
- [使用範例](../../../examples/ai_service_example.py)
- [OpenAI API 文檔](https://platform.openai.com/docs)

## 🆘 需要幫助？

如果遇到問題：
1. 運行快速測試：`python examples/quick_test_ai.py`
2. 檢查日誌輸出
3. 確認網路連接和 API Key

---

**祝你使用愉快！如果有任何問題，歡迎查看完整文檔或提出 Issue。**

