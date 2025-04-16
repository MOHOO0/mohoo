from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# ENV: ควรตั้งในระบบของ Render หรือ .env
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "Aiko (Command R+) is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "cohere/command-r-plus",  # ตรวจสอบชื่ออีกครั้งว่าเขียนถูก
        "messages": [
            {"role": "system", "content": "คุณคือ Aiko สาวญี่ปุ่นผู้ฉลาด สุภาพ และใจเย็น"},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and "choices" in response_data:
            ai_reply = response_data["choices"][0]["message"]["content"]
        else:
            print("❌ ERROR from OpenRouter:", response_data)
            ai_reply = "ขอโทษค่ะ Aiko มีปัญหากับโมเดล AI ตอนนี้ ลองใหม่อีกครั้งนะคะ 🙇‍♀️"
    except Exception as e:
        print("❌ Exception:", e)
        ai_reply = "เกิดข้อผิดพลาดบางอย่างค่ะ ลองใหม่อีกทีนะคะ 🥺"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )
