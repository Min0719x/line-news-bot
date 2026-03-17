import os
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 1. 讀取密鑰 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_ID = os.getenv("LINE_USER_ID")

# --- 2. 獲取情報邏輯 ---
def get_intelligence_report():
    try:
        genai.configure(api_key=GEMINI_KEY)
        # 修正：改用官方目前最穩定的名稱
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = """
你是位專業情報播報員，用最短的文字告訴我今天最重要的三件事。

格式（嚴格遵守）：
🚀 科技：一件大事 -> 影響
📈 市場：一個趨勢 -> 影響
⚠️ 危機：一個警訊 -> 影響

🌍 今日穩定度：X / 10
---
規則：全繁體中文，字數極簡，像朋友傳訊。
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[錯誤] Gemini 呼叫失敗: {e}"

# --- 3. 主程式 ---
def main():
    if not GEMINI_KEY or not LINE_TOKEN or not LINE_ID:
        print("❌ 缺少必要參數")
        return

    report_content = get_intelligence_report()
    
    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=report_content))
        print("✅ 任務完成")
    except Exception as e:
        print(f"❌ LINE 發送失敗: {e}")

if __name__ == "__main__":
    main()
