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

    # 2. 修正後的 HTTP 請求 URL
    # 在 v1 接口中，路徑必須包含 models/ 前綴才符合規範
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

        # 3. 檢查回傳狀態
        if response.status_code != 200:
            error_msg = response_data.get('error', {}).get('message', '未知錯誤')
            # 如果還是找不到，嘗試備用模型路徑
            raise Exception(f"Google API 報錯: {error_msg}")

        # 4. 提取文字內容
        if 'candidates' in response_data and response_data['candidates']:
            result_text = response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            result_text = "AI 成功回應，但內容為空 (可能是安全過濾)"

        # 5. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功！這一次路徑完全對準了。")

    except Exception as e:
        error_str = str(e)
        print(f"❌ 執行失敗：{error_str}")
        
        # 備援計畫：如果 flash 真的暫時不可用，這裡會提醒你
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=f"【路徑校對報錯】：\n{error_str}"))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
