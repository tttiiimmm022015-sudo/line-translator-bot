from google import genai

from config import GEMINI_API_KEY
from prompt import build_translation_prompt

client = genai.Client(api_key=GEMINI_API_KEY)


def translate(text: str) -> str:
    prompt = build_translation_prompt(text)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return response.text or "翻譯失敗，請稍後再試。"