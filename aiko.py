from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

# Flask app
app = Flask(__name__)

# อ่านค่า env จากระบบ Render
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Init LINE & OpenAI client
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)

# Route ทดสอบ
@app.route("/", methods=['GET'])
def home():
    return "Aiko is running!"

# Route สำหรับ webhook จาก LINE
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("Error in handler:", e)
        abort(500)

    return 'OK'

# เมื่อมีข้อความเข้ามาทาง LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # ขอคำตอบจาก OpenAI (เวอร์ชันใหม่)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "คุณคือ Aiko สาวญี่ปุ่น ขยัน ฉลาด รอบรู้ พูดจานุ่มนวล"},
            {"role": "user", "content": user_text}
        ]
    )

    reply_text = response.choices[0].message.content.strip()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# รันเซิร์ฟเวอร์ (เฉพาะ dev mode)
if __name__ == "__main__":
    app.run()
