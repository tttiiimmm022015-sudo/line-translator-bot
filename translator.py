import re

from google import genai
from google.genai.errors import ClientError

from config import GEMINI_API_KEY
from prompt import build_translation_prompt


client = genai.Client(api_key=GEMINI_API_KEY)


ERROR_MESSAGES = (
    "⚠️ 今日翻譯額度已用完",
    "⚠️ 翻譯服務暫時異常",
    "⚠️ 系統暫時異常",
    "⚠️ 翻譯失敗",
)


def translate_content(text: str) -> str:
    """
    呼叫 Gemini API 進行翻譯。
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=build_translation_prompt(text),
            config={
                "temperature": 0,
                "max_output_tokens": 256,
            },
        )

        translated_text = response.text

        if not translated_text:
            return "⚠️ 翻譯失敗，請稍後再試。"

        return translated_text.strip()

    except ClientError as error:
        error_message = str(error)

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
        ):
            return "⚠️ 今日翻譯額度已用完，請稍後再試。"

        print(f"Gemini API 錯誤：{error}")
        return "⚠️ 翻譯服務暫時異常，請稍後再試。"

    except Exception as error:
        print(f"未知錯誤：{error}")
        return "⚠️ 系統暫時異常，請稍後再試。"


def translate(
    text: str,
    display_name: str = "",
) -> str:
    """
    LINE Bot 主要翻譯函式。

    參數：
    text：
        使用者輸入的文字。

    display_name：
        發送者的 LINE 顯示名稱。
        沒有提供時不顯示名稱。

    回覆範例：

    👤 Pim

    TH → ZH-TW

    今天有客人嗎？
    """

    if not text:
        return "⚠️ 請輸入需要翻譯的內容。"

    text = text.strip()

    if not text:
        return "⚠️ 請輸入需要翻譯的內容。"

    direction = get_translation_direction(text)
    translated = translate_content(text)

    if translated.startswith(ERROR_MESSAGES):
        return translated

    if display_name:
        return (
            f"👤 {display_name}\n\n"
            f"{direction}\n\n"
            f"{translated}"
        )

    return (
        f"{direction}\n\n"
        f"{translated}"
    )
