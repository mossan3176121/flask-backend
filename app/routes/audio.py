from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.audio import AudioFile, Base
import os

bp = Blueprint("audio", __name__, url_prefix="/audio_data")

db_path = os.path.join(os.path.dirname(__file__), "../data/audio_files.db")
db_uri = f"sqlite:///file:{os.path.abspath(db_path)}?mode=ro&uri=true"

engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@bp.route("/all", methods=["GET"])
def get_audio_data():
    audio_data = session.query(AudioFile).all()
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
