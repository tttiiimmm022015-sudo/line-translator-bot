import os

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    UserSource,
    GroupSource,
    RoomSource,
)

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from translator import translate


configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(LINE_CHANNEL_SECRET)


def get_display_name(
    messaging_api: MessagingApi,
    event: MessageEvent,
) -> str:
    """
    依照訊息來源取得發送者的 LINE 顯示名稱。

    支援：
    - 一對一聊天
    - LINE 群組
    - 多人聊天室
    """

    source = event.source
    user_id = getattr(source, "user_id", None)

    if not user_id:
        return "未知使用者"

    try:
        # 一對一聊天
        if isinstance(source, UserSource):
            profile = messaging_api.get_profile(user_id)
            return profile.display_name or "未知使用者"

        # LINE 群組
        if isinstance(source, GroupSource):
            profile = messaging_api.get_group_member_profile(
                source.group_id,
                user_id,
            )
            return profile.display_name or "未知使用者"

        # 多人聊天室
        if isinstance(source, RoomSource):
            profile = messaging_api.get_room_member_profile(
                source.room_id,
                user_id,
            )
            return profile.display_name or "未知使用者"

    except Exception as error:
        # 名稱取得失敗時，翻譯功能仍然繼續
        print(f"取得 LINE 顯示名稱失敗：{error}")

    return "未知使用者"


@handler.add(
    MessageEvent,
    message=TextMessageContent,
)
def handle_text_message(event: MessageEvent):
    """
    收到文字訊息後：
    1. 取得發送者 LINE 名稱
    2. 翻譯文字
    3. 回覆翻譯結果
    """

    user_text = event.message.text.strip()

    if not user_text:
        return

    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)

        display_name = get_display_name(
            messaging_api,
            event,
        )

        reply_text = translate(
            text=user_text,
            display_name=display_name,
        )

        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=reply_text)
                ],
            )
        )
