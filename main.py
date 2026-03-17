import os
import sys
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 抓取環境變數 (請確保 GitHub Secrets 已設定 GROQ_API_KEY)
    groq_key = os.environ.get("GROQ_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not groq_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整，請檢查 GROQ_API_KEY, LINE_TOKEN, LINE_USER_ID")
        return

    # 2. 設定 Groq API (使用 Llama 3 8B 模型，穩定且免費)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    
    # 結合最初的「世界情報」意圖，設定 AI 的角色與任務
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": "你是一位專業的「全球情報分析師」。你的任務是篩選今日全球最重要的科技與商業情報，並以專業、簡潔的繁體中文進行總結。"
            },
            {
                "role": "user", 
                "content": "請分析今日全球科技動態，並提供 3-5 則最重要的情報摘要。要求：1. 繁體中文 2. 條列式呈現 3. 觀點犀利。"
            }
        ],
        "temperature": 0.7
    }

    try:
        # 發送請求
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result_text = response.json()['choices'][0]['message']['content']

        # 3. 格式化 LINE 訊息內容
        final_message = f"🌍 【世界情報】今日摘要：\n\n{result_text}"

        # 4. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=final_message))
        print("✅ 任務成功：世界情報已送達 LINE")

    except Exception as e:
        error_msg = f"❌ 系統執行異常：{str(e)}"
        print(error_msg)
        # 發生錯誤時同步通知 LINE
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=error_msg))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
