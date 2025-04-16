from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# ตั้งค่าจาก Environment Variables หรือใส่ตรงนี้ก็ได้
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_LINE_CHANNEL_SECRET")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_openrouter_api_key")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ฟังก์ชันเรียก OpenRouter + LLaMA 3

def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "คุณคือผู้ช่วย AI ที่พูดภาษาไทยได้อย่างเป็นธรรมชาติ ตอบอย่างสุภาพ ชัดเจน และตรงประเด็น"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return "⏳ ระบบตอบช้า กรุณาลองใหม่อีกครั้งนะคะ"

    except requests.exceptions.RequestException as e:
        return f"❌ เกิดข้อผิดพลาดกับระบบ AI: {str(e)}"

# Webhook หลักจาก LINE
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"[ERROR] Webhook error: {e}")
        abort(400)

    return "OK"

# เมื่อมีข้อความเข้ามา
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply_text = ask_openrouter(user_text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# รันแอป (ถ้า run ในเครื่อง local)
if __name__ == "__main__":
    app.run(debug=True, port=5000)
