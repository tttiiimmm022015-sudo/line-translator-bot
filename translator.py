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
    只負責呼叫 Gemini 翻譯。
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

        if not response.text:
            return "⚠️ 翻譯失敗，請稍後再試。"

        return response.text.strip()

    except ClientError as error:
        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return "⚠️ 今日翻譯額度已用完，請稍後再試。"

        print(f"Gemini API 錯誤：{error}")
        return "⚠️ 翻譯服務暫時異常，請稍後再試。"

    except Exception as error:
        print(f"未知錯誤：{error}")
        return "⚠️ 系統暫時異常，請稍後再試。"


def translate(text: str, display_name: str = "") -> str:
    """
    LINE Bot 呼叫的主要翻譯函式。

    text:
        使用者輸入的文字

    display_name:
        發送者的 LINE 顯示名稱
    """

    text = text.strip()

    if not text:
        return "⚠️ 請輸入需要翻譯的內容。"

    translated = translate_content(text)

    # 翻譯發生錯誤時，直接回傳錯誤訊息
    if translated.startswith(ERROR_MESSAGES):
        return translated

    if display_name:
        return f"🤖 翻譯 {display_name}\n\n{translated}"

    return f"🤖 翻譯\n\n{translated}"
