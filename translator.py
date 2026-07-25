from google import genai
from google.genai.errors import ClientError

from config import GEMINI_API_KEY
from prompt import build_translation_prompt


# 建立 Gemini 用戶端
client = genai.Client(
    api_key=GEMINI_API_KEY,
)


MODEL_NAME = "gemini-3.1-flash-lite"


def translate(text: str) -> str:
    """
    將繁體中文翻譯成泰文，
    或將泰文翻譯成繁體中文。

    本函式只回傳翻譯結果，
    不加入翻譯方向、LINE 名稱或其他標題。
    """

    if not text:
        return "⚠️ 請輸入需要翻譯的內容。"

    text = text.strip()

    if not text:
        return "⚠️ 請輸入需要翻譯的內容。"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
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
            print(f"Gemini API 額度不足：{error}")
            return "⚠️ 今日翻譯額度已用完，請稍後再試。"

        if "404" in error_message:
            print(f"Gemini 模型不存在或已停用：{error}")
            return "⚠️ 翻譯模型暫時無法使用。"

        print(f"Gemini API 錯誤：{error}")
        return "⚠️ 翻譯服務暫時異常，請稍後再試。"

    except Exception as error:
        print(f"翻譯時發生未知錯誤：{error}")
        return "⚠️ 系統暫時異常，請稍後再試。"
