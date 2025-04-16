from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# 🛡️ ใส่ TOKEN ที่คุณได้จาก LINE Developer
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_LINE_SECRET")

# 🔐 ใส่ API KEY จาก OpenRouter (https://openrouter.ai)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    # 📦 เตรียม request สำหรับ OpenRouter (Command R+)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",  # เปลี่ยนให้ตรงกับโดเมนของคุณ
        "X-Title": "Aiko Bot"
    }

    data = {
        "model": "cohere/command-r-plus",
        "max_tokens": 1024,  # ปรับให้ไม่เกินโควต้า
        "messages": [
            {"role": "system", "content": "คุณคือ Aiko สาวญี่ปุ่นผู้ฉลาด สุภาพ และใจเย็น"},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()

        if "choices" in response_data:
            ai_reply = response_data["choices"][0]["message"]["content"]
        else:
            ai_reply = "❌ เกิดข้อผิดพลาดจากฝั่ง AI: " + response_data.get("error", {}).get("message", "ไม่ทราบสาเหตุ")

    except Exception as e:
        ai_reply = f"⚠️ เกิดข้อผิดพลาด: {str(e)}"

    # 📤 ส่งกลับไปยัง LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )

if __name__ == "__main__":
    app.run()
