import os
import google.generativeai as genai
from linebot import LineBotApi
from linebot.models import TextSendMessage

def run_bot():
    # 1. 從環境變數讀取金鑰
    gemini_key = os.environ.get("GEMINI_API_KEY")
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get("LINE_USER_ID")

    if not all([gemini_key, line_token, line_user_id]):
        print("錯誤：環境變數設定不完整")
        return

    # 2. 設定 Gemini (關鍵修復：路徑與版本)
    genai.configure(api_key=gemini_key)
    # 使用正確的模型名稱字串
    model = genai.GenerativeModel('gemini-1.5-flash')

    try:
        # 這裡放入你想要 AI 總結的指令或抓取的資料
        prompt = "請幫我總結今日的全球重要科技新聞，並以繁體中文條列式呈現。"
        
        response = model.generate_content(prompt)
        result_text = response.text

        # 3. 推送訊息到 LINE
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=result_text))
        print("訊息發送成功！")

    except Exception as e:
        error_msg = f"執行失敗：{str(e)}"
        print(error_msg)
        # 報錯也傳給 LINE，方便調試
        line_bot_api = LineBotApi(line_token)
        line_bot_api.push_message(line_user_id, TextSendMessage(text=error_msg))

if __name__ == "__main__":
    run_bot()
