import os
import sys
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    try:
        # 1. 從環境變數讀取金鑰
        gemini_key = os.environ.get("GEMINI_API_KEY")
        line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        line_user_id = os.environ.get("LINE_USER_ID")

        # 檢查變數是否缺失
        missing_vars = []
        if not gemini_key: missing_vars.append("GEMINI_API_KEY")
        if not line_token: missing_vars.append("LINE_CHANNEL_ACCESS_TOKEN")
        if not line_user_id: missing_vars.append("LINE_USER_ID")
        
        if missing_vars:
            print(f"錯誤：缺少環境變數 {', '.join(missing_vars)}")
            return

        # 2. 設定 Gemini (修正 404 問題)
        genai.configure(api_key=gemini_key)
        # 鎖定穩定版模型名稱
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. 產生內容
        prompt = "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"
        response = model.generate_content(prompt)
        result_text = response.text

        # 4. 推送訊息到 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功：訊息已發送到 LINE")

    except Exception as e:
        error_msg = f"❌ 執行失敗：{str(e)}"
        print(error_msg)
        # 嘗試將錯誤訊息發送到 LINE
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=error_msg))
        except:
            pass
        sys.exit(1) # 讓 GitHub Actions 標記為失敗以利觀察

if __name__ == "__main__":
    run_bot()
