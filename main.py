import os
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 從 GitHub Secrets 讀取密鑰
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_ID    = os.environ["LINE_USER_ID"]

MAX_LINE_LENGTH = 4900

def get_intelligence_report():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    你是一位情報播報員，用最短的文字告訴我今天最重要的三件事。

    格式（嚴格遵守）：
    📡 科技：一句話事件 → 一句話影響
    📈 市場：一句話事件 → 一句話影響
    ⚠️ 危機：一句話事件 → 一句話影響

    🌍 今日穩定度：X／10　理由：一句話

    規則：
    - 全文不超過 150 字
    - 繁體中文
    - 像朋友傳訊息，不像新聞稿
    """

    response = model.generate_content(prompt)
    return response.text

def main():
    try:
        report_content = get_intelligence_report()
    except Exception as e:
        print(f"[錯誤] Gemini API 呼叫失敗: {e}")
        return

    if len(report_content) > MAX_LINE_LENGTH:
        report_content = report_content[:MAX_LINE_LENGTH] + "\n\n[訊息過長，已截斷]"

    try:
        line_bot = LineBotApi(LINE_TOKEN)
        line_bot.push_message(LINE_ID, TextSendMessage(text=report_content))
        print("情報分析任務完成，訊息已送達 LINE。")
    except Exception as e:
        print(f"[錯誤] LINE 訊息發送失敗: {e}")

if __name__ == "__main__":
    main()
