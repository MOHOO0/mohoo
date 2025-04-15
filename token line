from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(name)

ตั้งค่า Token จาก LINE
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_LINE_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_LINE_CHANNEL_SECRET'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

ตั้งค่า OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"

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
    user_message = event.message.text
    # ส่งข้อความไปยัง GPT เพื่อให้ Aiko ตอบ
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # หรือ gpt-4
        messages=[
            {"role": "system", "content": "คุณคือ Aiko สาวญี่ปุ่นขยันและรอบรู้"},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response.choices[0].message['content']
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if name == "main":
    app.run()
