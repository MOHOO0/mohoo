```python
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

ดึงค่าจาก environment variables ที่ตั้งไว้บน Render
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('2007269330')
LINE_CHANNEL_SECRET = os.getenv('202dc283533367d627729fac8916a2ef')
OPENAI_API_KEY = os.getenv('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')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=['GET'])
def home():
    return "Aiko is running!"

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
    user_text = event.message.text

    # สั่งให้ GPT ตอบในฐานะ Aiko
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "คุณคือ Aiko สาวญี่ปุ่น ขยัน ฉลาด รอบรู้ พูดจานุ่มนวล"},
            {"role": "user", "content": user_text}
        ]
    )

    reply_text = response['choices'][0]['message']['content']
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if name == "main":
    app.run()
```
