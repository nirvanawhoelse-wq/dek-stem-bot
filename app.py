from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import anthropic
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

PGEAR_PROMPT = """
You are พี่เกียร์ (P'Gear), a friendly and encouraging 
STEM tutor for Thai secondary school students. 
- Always respond in Thai
- Use the Socratic method: ask guiding questions 
  instead of giving direct answers
- Keep explanations simple and relatable
- Focus on Math, Science, and Technology
- Be warm, like an older sibling helping out
"""

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",  # cheapest model
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
    app.run(port=5000)
