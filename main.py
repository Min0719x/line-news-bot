import os
import sys
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 獲取環境變數
    api_key = os.environ.get("GEMINI_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not api_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整")
        return

    # 2. 直接使用 HTTP 請求調用 Gemini V1 正式版接口
    # 這樣可以完全繞過 v1beta 的 404 錯誤
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # 檢查是否報錯
        if response.status_code != 200:
            error_msg = response_data.get('error', {}).get('message', '未知錯誤')
            raise Exception(f"Google API 報錯: {error_msg}")

        # 提取文字內容
        result_text = response_data['candidates'][0]['content']['parts'][0]['text']

        # 3. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功！終於繞過 404 了！")

    except Exception as e:
        error_str = str(e)
        print(f"❌ 執行失敗：{error_str}")
        # 報錯傳給 LINE
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=f"【HTTP 直連報錯】：\n{error_str}"))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
