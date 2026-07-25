from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    GroupSource,
    MessageEvent,
    RoomSource,
    TextMessageContent,
    UserSource,
)

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from translator import translate


# LINE Messaging API 設定
configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)

# Webhook Handler
handler = WebhookHandler(LINE_CHANNEL_SECRET)


def get_display_name(
    messaging_api: MessagingApi,
    event: MessageEvent,
) -> str:
    """
    取得訊息發送者的 LINE 顯示名稱。

    支援：
    - 一對一聊天
    - LINE 群組
    - 多人聊天室

    取得失敗時回傳空字串，
    翻譯仍可正常執行，但不顯示名稱。
    """

    source = event.source
    user_id = getattr(source, "user_id", None)

    if not user_id:
        return ""

    try:
        # 一對一聊天
        if isinstance(source, UserSource):
            profile = messaging_api.get_profile(user_id)
            return profile.display_name or ""

        # LINE 群組
        if isinstance(source, GroupSource):
            profile = messaging_api.get_group_member_profile(
                group_id=source.group_id,
                user_id=user_id,
            )
            return profile.display_name or ""

        # 多人聊天室
        if isinstance(source, RoomSource):
            profile = messaging_api.get_room_member_profile(
                room_id=source.room_id,
                user_id=user_id,
            )
            return profile.display_name or ""

    except Exception as error:
        # 取得名稱失敗不影響翻譯
        print(f"取得 LINE 顯示名稱失敗：{error}")

    return ""


@handler.add(
    MessageEvent,
    message=TextMessageContent,
)
def handle_text_message(event: MessageEvent) -> None:
    """
    收到文字訊息後：

    1. 讀取訊息內容
    2. 取得發送者的 LINE 顯示名稱
    3. 呼叫 Gemini 翻譯
    4. 回覆翻譯結果
    """

    user_text = event.message.text.strip()

    if not user_text:
        return

    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            display_name = get_display_name(
                messaging_api=messaging_api,
                event=event,
            )

            reply_text = translate(
                text=user_text,
                display_name=display_name,
            )

            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                        )
                    ],
                )
            )

    except Exception as error:
        print(f"處理 LINE 訊息失敗：{error}")
