from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app, origins=["https://adicteng.com", "http://127.0.0.1:5000"], supports_credentials=True, methods=["POST", "GET", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

    from .routes import audio, subtitles, chat, correct, translate
    app.register_blueprint(audio.bp)
    app.register_blueprint(subtitles.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(correct.bp)
    app.register_blueprint(translate.bp)

    return app
