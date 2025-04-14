from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.audio import AudioFile, Base
import os

bp = Blueprint("audio", __name__, url_prefix="/audio_data/all")

db_path = os.path.join(os.path.dirname(__file__), "../data/audio_files.db")
db_uri = f"sqlite:///file:{os.path.abspath(db_path)}?mode=ro&uri=true"

engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@bp.route("", methods=["GET", "OPTIONS"])
def get_audio_data():
    try:
        audio_data = session.query(AudioFile).all()
        print("📢 audio_data の件数:", len(audio_data))  # ← 追加
        return jsonify([
            {
                "id": file.id,
                "verb": file.verb,
                "verb_jp": file.verb_jp,
                "sentence": file.sentence,
                "sentence_jp": file.sentence_jp,
                "path": file.path
            } for file in audio_data
        ])
    except Exception as e:
        print("🔥 /all エラー:", e)
        return jsonify({"error": "サーバー側でエラーが発生しました"}), 500

