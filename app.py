from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import re
import traceback
from youtube_transcript_api import YouTubeTranscriptApi

# SQLAlchemy関連
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app)

### ---------- SQLite /audio_data/all 用 ----------
# SQLite のデータベース設定 (読み取り専用)
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
db_uri = f"sqlite:///file:{db_path}?mode=ro&uri=true"

# SQLAlchemyの設定
engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# モデル定義
class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True)
    verb = Column(Text, nullable=False)
    verb_jp = Column(Text, nullable=False)
    sentence = Column(Text, nullable=False)
    sentence_jp = Column(Text, nullable=False)
    path = Column(Text, nullable=False)

@app.route("/audio_data/all", methods=["GET"])
def get_audio_data():
    audio_data = session.query(AudioFile).all()
    if audio_data:
        audio_data = [{
            "id": file.id,
            "verb": file.verb,
            "verb_jp": file.verb_jp,
            "sentence": file.sentence,
            "sentence_jp": file.sentence_jp,
            "path": file.path
        } for file in audio_data]
        return app.response_class(
            response=json.dumps(audio_data, ensure_ascii=False, indent=4),
            status=200,
            mimetype="application/json"
        )
    return jsonify({"error": "File not found"}), 404


### ---------- YouTube字幕取得 /get_subtitles 用 ----------

def extract_video_id(url):
    pattern = r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route("/get_subtitles", methods=["POST"])
def get_subtitles():
    data = request.get_json()
    url = data.get("url")
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        raw_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        clean_transcript = clean_transcript_basic(raw_transcript)
        return jsonify({"transcript": clean_transcript})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def clean_transcript_basic(raw_transcript):
    clean_sentences = []
    filtered = [entry for entry in raw_transcript if not re.match(r'^\[.*\]$', entry['text'].strip())]

    for i, entry in enumerate(filtered):
        text = entry['text'].strip()
        start = round(entry['start'], 2)
        end = round(filtered[i + 1]['start'], 2) if i < len(filtered) - 1 else round(entry['start'] + entry['duration'], 2)

        clean_sentences.append({
            "text": text,
            "start": start,
            "end": end
        })

    return clean_sentences


### ---------- Flask 起動 ----------
if __name__ == "__main__":
    app.run(debug=True)
