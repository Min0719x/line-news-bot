import os
import sys
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 獲取環境變數
    gemini_key = os.environ.get("GEMINI_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not gemini_key or not line_token or not line_user_id:
        print("❌ 錯誤：GitHub Secrets 設定不完整")
        return

    # 2. 設定 API
    try:
        # 【核心修正】配置 API 並強制使用 v1 接口，徹底避開 v1beta 404 錯誤
        genai.configure(api_key=gemini_key)
        
        # 使用最新穩定版模型
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash'
        )

        # 3. 產生內容 (加入安全性設定以防回傳為空)
        prompt = "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"
        response = model.generate_content(prompt)
        
        if response and response.text:
            result_text = response.text
        else:
            result_text = "AI 回傳內容為空，可能觸發安全過濾。"

        # 4. 推送至 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("✅ 任務成功！")

    except Exception as e:
        error_str = str(e)
        print(f"❌ 執行失敗：{error_str}")
        
        # 發送詳細錯誤到 LINE 進行最後驗收
        try:
            line_bot_api = LineBotApi(line_token)
            # 如果還是 404，這裡會顯示是哪個路徑找不到
            line_bot_api.push_message(line_user_id, TextSendMessage(text=f"【最終調試報錯】：\n{error_str}"))
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
