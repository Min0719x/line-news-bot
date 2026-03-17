import os
import google.generativeai as genai

# 設定 Gemini API
# 這裡建議使用環境變數，若測試用也可直接填入字串
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_response(prompt):
    try:
        # 【關鍵修復】使用穩定的模型名稱，不帶 models/ 前綴，避免 v1beta 歧義
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 呼叫失敗: {str(e)}"

# 這裡加入你原本處理 LINE 訊息的邏輯...
# 確保在調用 generate_content 時，模型定義如上所示
