import re

from google import genai
from google.genai.errors import ClientError

from config import GEMINI_API_KEY
from prompt import build_translation_prompt


client = genai.Client(api_key=GEMINI_API_KEY)


def split_speaker(text: str) -> tuple[str | None, str]:
    """
    拆分說話者名稱與翻譯內容。

    支援格式：
    A小姐：今天有上班嗎？
    A小姐: 今天有上班嗎？
    Pim：วันนี้มาทำงานไหม
    @Momay：客人在找你

    如果沒有「：」或「:」，就視為沒有指定說話者。
    """

    text = text.strip()

    match = re.match(
        r"^([^：:\n]{1,30})[：:]\s*(.+)$",
        text,
        flags=re.DOTALL,
    )

    if not match:
        return None, text

    speaker = match.group(1).strip()
    content = match.group(2).strip()

    # 避免把「19:00 有客人」誤認成：
    # 說話者 = 19
    # 內容 = 00 有客人
    if speaker.replace(" ", "").isdigit():
        return None, text

    # 防止冒號後面沒有內容
    if not content:
        return None, text

    return speaker, content


def translate_content(text: str) -> str:
    """
    只負責呼叫 Gemini 翻譯，不處理說話者名稱。
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


def translate(text: str) -> str:
    """
    LINE Bot 使用的主要翻譯函式。

    有說話者：
    A小姐：今天有上班嗎？

    回覆：
    🤖 翻譯 A小姐

    วันนี้มาทำงานไหม

    沒有說話者：
    今天有上班嗎？

    回覆：
    วันนี้มาทำงานไหม
    """

    if not text or not text.strip():
        return "⚠️ 請輸入需要翻譯的內容。"

    speaker, content = split_speaker(text)

    translated = translate_content(content)

    # 發生錯誤時直接顯示錯誤，不附加「翻譯某某」
    if translated.startswith("⚠️"):
        return translated

    if speaker:
        return f"🤖 翻譯 {speaker}\n\n{translated}"

    return translated
