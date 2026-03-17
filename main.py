import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 1. 讀取密鑰 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_ID = os.getenv("LINE_USER_ID")

def get_intelligence():
    try:
        # --- 2. 抓取 World Monitor 內容 ---
        url = "https://world-monitor.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 獲取網頁前 2500 字
        web_text = soup.get_text()[:2500]

        # --- 3. 呼叫 Gemini (修正 404 問題的寫法) ---
        genai.configure(api_key=GEMINI_KEY)
        
        # 這是最穩定的模型標識符，不要加任何 "models/" 前綴
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
你是一位專業情報官。請根據以下網頁內容，整理出今日最核心的三則情報：
網頁內容：{web_text}

---
格式要求（繁體中文）：
🚀 科技/軍事：[一件大事] -> [影響]
📈 市場/經濟：[一個趨勢] -> [影響]
⚠️ 危機/衝突：[一個警訊] -> [影響]

🌍 今日穩定度：X / 10
---
規則：字數精簡，像私人情報簡訊，不要有廢話。
"""
        # 使用最新的生成方法
        result = model.generate_content(prompt)
        return result.text

    except Exception as e:
        # 如果還是失敗，回傳具體錯誤訊息到 LINE 方便偵錯
        return f"❌ 執行失敗：{str(e)}"

def main():
    if not all([GEMINI_KEY, LINE_TOKEN, LINE_ID]):
        print("❌ 密鑰不完整")
        return

    print("🛰️ 正在連線至 World Monitor 並進行分析...")
    report = get_intelligence()
    
    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=report))
        print("✅ 任務成功")
    except Exception as e:
        print(f"❌ LINE 發送錯誤: {e}")

if __name__ == "__main__":
    main()
