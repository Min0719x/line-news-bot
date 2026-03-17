import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 1. 密鑰讀取 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_ID = os.getenv("LINE_USER_ID")

# --- 2. 核心抓取與 AI 邏輯 ---
def get_world_monitor_intelligence():
    try:
        # 抓取目標網址內容
        url = "https://world-monitor.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 取得網頁純文字（前 2000 字以防超出 AI 限制）
        web_text = soup.get_text()[:2000]

        # 設定 Gemini
        genai.configure(api_key=GEMINI_KEY)
        # 修正：直接使用 'gemini-1.5-flash'，這是目前最通用的路徑
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
請根據以下網頁內容，整理出今天最重要的三則全球情報：
網頁內容：{web_text}

格式要求：
🚀 科技/軍事：一件大事 -> 影響
📈 市場/經濟：一個趨勢 -> 影響
⚠️ 危機/衝突：一個警訊 -> 影響

🌍 今日穩定度評分：X / 10
---
規則：全繁體中文，像朋友傳訊息，不要廢話。
"""
        result = model.generate_content(prompt)
        return result.text
    except Exception as e:
        return f"❌ 抓取或 AI 分析失敗: {str(e)}"

# --- 3. 主程式 ---
def main():
    if not all([GEMINI_KEY, LINE_TOKEN, LINE_ID]):
        print("❌ 密鑰不完整，請檢查 GitHub Secrets")
        return

    print("🛰️ 正在連線至 World Monitor 並進行 AI 分析...")
    report = get_world_monitor_intelligence()
    
    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=report))
        print("✅ 情報已送達 LINE")
    except Exception as e:
        print(f"❌ LINE 發送錯誤: {e}")

if __name__ == "__main__":
    main()
