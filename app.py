import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import anthropic

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

PGEAR_PROMPT = """
You are P'Gear, a friendly STEM tutor for Thai students.
Always respond in Thai.
Use the Socratic method.
Focus on Math, Science, and Technology.
Be warm and encouraging.
"""

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'OK', 200
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception:
        abort(400)
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=PGEAR_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    reply = response.content[0].text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
