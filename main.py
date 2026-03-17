import os
import sys
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 抓取環境變數
    gemini_key = os.environ.get("GEMINI_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not gemini_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整，請檢查 GEMINI_API_KEY, LINE_TOKEN, LINE_USER_ID")
        return

    # 2. 強制設定 API 版本與模型 (解決 404 核心)
    try:
        # 配置 API Key
        genai.configure(api_key=gemini_key)
        
        # 【關鍵修改】直接指定模型名稱，不加 models/ 前綴
        # 如果 v1beta 持續報錯，SDK 會自動嘗試穩定版路徑
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. 測試生成內容
        prompt = "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"
        response = model.generate_content(prompt)
        
        # 檢查 response 是否有效
        if response and response.text:
            result_text = response.text
        else:
            result_text = "AI 回傳內容為空，請檢查 API 額度或內容安全設定。"

        # 4. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功！")

    except Exception as e:
        error_str = str(e)
        print(f"❌ 執行失敗：{error_str}")
        
        # 將錯誤詳細資訊傳回 LINE 方便我們除錯
        try:
            line_bot_api = LineBotApi(line_token)
            line_bot_api.push_message(line_user_id, TextSendMessage(text=f"系統報錯詳情：\n{error_str}"))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
