from flask import Flask, request, abort, g

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    StickerMessageContent
)

import json, uuid
from log_service import LogService
from mqtt.publisher import MQClient
import os

mqClient = MQClient()
mqClient.start()

app = Flask(__name__)

LINEBOT_ACCESS_TOKEN = os.getenv("LINEBOT_ACCESS_TOKEN")
LINEBOT_CHANNEL_SECRET = os.getenv("LINEBOT_CHANNEL_SECRET")

configuration = Configuration(access_token=LINEBOT_ACCESS_TOKEN)
handler = WebhookHandler(LINEBOT_CHANNEL_SECRET)

fail_message = "只接受文字訊息!!"
fail_message_over_length = "訊息長度超過限制!! 最多20個字元!!"

def get_db():
    if 'db' not in g:
        g.db = LogService()  # 使用單例資料庫連接
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/test")
def test():
    mqClient.publish("Hello, WORLD!")
    return "ok"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    raw = request.get_data(as_text=True)

    # handle webhook body
    try:
        get_db().store_message(raw)
        store_message(raw)
        handler.handle(raw, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message:TextMessageContent = event.message
        if (message.emojis is not None):
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=fail_message)]
                )
            )
            return
        if (message.text.__len__() > 20):
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=fail_message_over_length)]
                )
            )
            return
        mqClient.publish(message.text)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'已投放 "{message.text}" 到螢幕上囉!!')]
            )
        )

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=fail_message)]
                )
            )

def store_message(message: str):
    events:list = json.loads(message).get("events")
    if (events.__len__() > 0):
        for event in events:
            event:dict
            user_id = uuid.uuid4()
            source:dict = event.get("source")
            if ("type" in source and source.get("type") == "user"):
                user_id = source.get("userId")
            timestamp = event.get("timestamp")
            with open(f"./events/{user_id}_{timestamp}.json", "w") as f:
                f.write(json.dumps(event, indent=4))
                f.close()
    

def initialize_folders():
    # Create folder
    import os
    if not os.path.exists("./events"):
        os.makedirs("./events")
    if not os.path.exists("./sqlite"):
        os.makedirs("./sqlite")
    pass


if __name__ == "__main__":
    initialize_folders()
    app.run(host="0.0.0.0", port=8080)
    mqClient.close()