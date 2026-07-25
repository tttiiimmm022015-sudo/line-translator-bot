def build_translation_prompt(text: str) -> str:
    return f"""
請判斷下面內容是繁體中文還是泰文，並翻譯成另一種語言。

規則：
- 中文翻譯成泰文
- 泰文翻譯成繁體中文
- 只輸出翻譯結果
- 不要解釋
- 不要加標題
- 保留原本語氣

內容：
{text}
"""