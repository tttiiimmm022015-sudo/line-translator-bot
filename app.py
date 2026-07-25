from flask import Flask, request

from line_handler import handler

app = Flask(__name__)


@app.route("/")
def home():
    return "LINE Translator Bot is running!"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")

    body = request.get_data(as_text=True)

    handler.handle(body, signature)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True)