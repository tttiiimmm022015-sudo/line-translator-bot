from google import genai
from google.genai.errors import ClientError

from config import GEMINI_API_KEY
from prompt import build_translation_prompt


client = genai.Client(api_key=GEMINI_API_KEY)


def translate(text: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=build_translation_prompt(text),
            config={
                "temperature": 0,
                "max_output_tokens": 256,
            },
        )

        return response.text or "翻譯失敗，請稍後再試。"

    except ClientError as error:
        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return "⚠️ 今日翻譯額度已用完，請稍後再試。"

        print(f"Gemini API 錯誤：{error}")
        return "⚠️ 翻譯服務暫時異常，請稍後再試。"

    except Exception as error:
        print(f"未知錯誤：{error}")
        return "⚠️ 系統暫時異常，請稍後再試。"
