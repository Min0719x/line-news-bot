import os
import sys
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 獲取你剛剛設定好的金鑰
    api_key = os.environ.get("GEMINI_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not api_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整")
        return

    # 2. 強制使用 v1beta 接口，這是目前最穩定的路徑
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"}]
        }]
    }

    try:
        # 直接發送請求給 Google
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # 檢查 Google 是否有噴錯誤
        if response.status_code != 200:
            error_msg = response_data.get('error', {}).get('message', '未知錯誤')
            raise Exception(f"Google 伺服器報錯: {error_msg}")

        # 成功拿回文字
        result_text = response_data['candidates'][0]['content']['parts'][0]['text']

        # 3. 傳送到 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功！")

    except Exception as e:
        error_str = str(e)
        print(f"❌ 執行失敗：{error_str}")
        # 如果失敗，也把原因傳到 LINE 讓你知道
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=f"【系統最終修正報錯】：\n{error_str}"))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
