import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# --- 1. 讀取密鑰 (從 GitHub Secrets) ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_ID = os.getenv("LINE_USER_ID")

# --- 2. 核心：抓取 World Monitor 並讓 AI 分析 ---
def get_intelligence():
    try:
        # 1. 抓取網頁內容
        target_url = "https://world-monitor.com/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        # 2. 解析網頁文字
        soup = BeautifulSoup(response.text, 'html.parser')
        # 抓取網頁中的文字，並截取前 2500 字給 AI
        web_content = soup.get_text()[:2500]

        # 3. 設定 Gemini AI
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
你是一位頂尖情報分析官。請針對以下來自 World Monitor 的網頁內容進行深度總結：

網頁資料：
{web_content}

---
請嚴格按照以下格式回報（全繁體中文）：
🚀 科技/軍事：[一件大事] -> [影響]
📈 市場/經濟：[一個趨勢] -> [影響]
⚠️ 危機/衝突：[一個警訊] -> [影響]

🌍 今日穩定度：X / 10
---
規則：字數精簡，像私人情報簡訊，不要有廢話。
"""
        # 4. 產生內容
        ai_response = model.generate_content(prompt)
        return ai_response.text

    except Exception as e:
        return f"❌ 系統執行失敗：{str(e)}"

# --- 3. 執行與發送 ---
def main():
    # 檢查密鑰是否齊全
    if not all([GEMINI_KEY, LINE_TOKEN, LINE_ID]):
        print("❌ 錯誤：GitHub Secrets 密鑰設定不完整")
        return

    print("🛰️ 正在抓取 World Monitor 最新情報並進行分析...")
    final_report = get_intelligence()
    
    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=final_report))
        print("✅ 任務成功：情報已送達你的 LINE")
    except Exception as e:
        print(f"❌ LINE 發送失敗：{e}")

if __name__ == "__main__":
    main()
