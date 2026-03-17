import os
import sys
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 獲取環境變數
    groq_key = os.environ.get("GROQ_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not groq_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整 (請檢查 GROQ_API_KEY)")
        return

    # 2. 調用 Groq API (使用 Llama 3 模型)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": "你是一個專業的新聞摘要助手，請用繁體中文回答。"
            },
            {
                "role": "user", 
                "content": "請幫我總結今日全球最重要的科技新聞，以繁體中文條列式呈現。"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result_text = response.json()['choices'][0]['message']['content']

        # 3. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功：Groq 訊息已發送")

    except Exception as e:
        error_str = f"❌ Groq 執行失敗：{str(e)}"
        print(error_str)
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=error_str))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
