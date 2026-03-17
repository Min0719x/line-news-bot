import os
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 1. 鑰匙讀取與偵錯邏輯 ---
# 嘗試抓取所有可能的名字
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_ID = os.getenv("LINE_USER_ID")

def check_env():
    print("--- 環境變數檢查 ---")
    print(f"Gemini Key 存在: {'✅ 是' if GEMINI_KEY else '❌ 否'}")
    print(f"Line Token 存在: {'✅ 是' if LINE_TOKEN else '❌ 否'}")
    print(f"Line UserID 存在: {'✅ 是' if LINE_ID else '❌ 否'}")
    if not GEMINI_KEY:
        print("!! 警告：找不到 Gemini API Key，請檢查 GitHub Secrets 是否設定名稱為 GEMINI_API_KEY")

# --- 2. 獲取情報邏輯 ---
def get_intelligence_report():
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
你是位情報播報員，用最短的文字告訴我今天最重要的三件事。

格式（嚴格遵守）：
🚀 科技：一句話事件 -> 一句話影響
📈 市場：一句話事件 -> 一句話影響
⚠️ 危機：一句話事件 -> 一句話影響

🌍 今日穩定度：X / 10  理由：一句話
---
規則：
- 全文不超過 150 字
- 繁體中文
- 像朋友傳訊息，不像新聞稿
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[錯誤] Gemini 呼叫失敗: {e}"

# --- 3. 主程式 ---
def main():
    check_env()
    
    if not GEMINI_KEY or not LINE_TOKEN or not LINE_ID:
        print("❌ 缺少必要參數，停止運行。")
        return

    report_content = get_intelligence_report()
    
    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=report_content))
        print("✅ 情報分析任務完成，訊息已送達 LINE。")
    except Exception as e:
        print(f"❌ [錯誤] LINE 訊息發送失敗: {e}")

if __name__ == "__main__":
    main()
