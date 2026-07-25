import re

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    Sender,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from translator import translate


configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(LINE_CHANNEL_SECRET)


def detect_translation_direction(text: str) -> str:
    """
    判斷翻譯方向，作為 LINE 訊息上方顯示名稱。

    中文 → 泰文：ZH-TW→TH
    泰文 → 中文：TH→ZH-TW
    """

    thai_count = len(
        re.findall(r"[\u0E00-\u0E7F]", text)
    )

    chinese_count = len(
        re.findall(r"[\u3400-\u4DBF\u4E00-\u9FFF]", text)
    )

    if thai_count > chinese_count and thai_count > 0:
        return "TH→ZH-TW"

    if chinese_count > 0:
        return "ZH-TW→TH"

    if thai_count > 0:
        return "TH→ZH-TW"

    return "Translator"


@handler.add(
    MessageEvent,
    message=TextMessageContent,
)
def handle_text_message(event: MessageEvent) -> None:
    """
    收到文字訊息後：

    1. 判斷翻譯方向
    2. 呼叫翻譯函式
    3. 將翻譯方向顯示在訊息發送者名稱
    4. 回覆翻譯結果
    """

    user_text = event.message.text.strip()

    if not user_text:
        return

    try:
        translation_direction = detect_translation_direction(
            user_text
        )

        # translator.py 現在只需回傳翻譯結果
        reply_text = translate(user_text)

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            sender=Sender(
                                name=translation_direction,
                            ),
                        )
                    ],
                )
            )

    except Exception as error:
        print(f"處理 LINE 訊息失敗：{error}")
