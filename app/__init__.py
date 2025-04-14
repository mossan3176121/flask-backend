from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os


URL = "https://adicteng.com"
# URL = "*"
def create_app():
    load_dotenv()

    app = Flask(__name__)

    # ✅ CORSの設定をより厳密に、複数Origin対応で動作する形に修正
    CORS(app,
         resources={r"/*": {"origins": URL}},
         supports_credentials=True,
         methods=["POST", "GET", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])

    from .routes import audio, subtitles, chat, correct, translate, mini_conversation
    app.register_blueprint(audio.bp)
    app.register_blueprint(subtitles.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(correct.bp)
    app.register_blueprint(translate.bp)
    app.register_blueprint(mini_conversation.bp)

    return app
