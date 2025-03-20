from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
import json
import re
import traceback

# .env読み込み
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = Flask(__name__)
CORS(app, origins=["https://adicteng.com"], supports_credentials=True, methods=["POST"])


# ========== OpenAI 設定 ==========
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# キャラクター設定
character_prompts = {
    "tutor": "You are a kind and patient English tutor...",
    "friend": "You are the user's friendly English-speaking friend...",
    "lover": "You are the user's English-speaking romantic partner...",
    "boss": "You are a professional business manager...",
    "airport": "You are an airport staff member helping a traveler...",
    "waiter": "You are a cheerful waiter or waitress at a café...",
    "random": "You are a friendly English speaker..."
}

# ========== SQLite（/audio_data/all）設定 ==========
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
db_uri = f"sqlite:///file:{db_path}?mode=ro&uri=true"

engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

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
    return jsonify({"error": "File not found"}), 404

# ========== YouTube字幕取得（/get_subtitles） ==========
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
        return jsonify({"transcript": clean_transcript_basic(raw_transcript)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def clean_transcript_basic(raw_transcript):
    filtered = [entry for entry in raw_transcript if not re.match(r'^\[.*\]$', entry['text'].strip())]
    return [
        {
            "text": entry['text'].strip(),
            "start": round(entry['start'], 2),
            "end": round(filtered[i + 1]['start'], 2) if i < len(filtered) - 1 else round(entry['start'] + entry['duration'], 2)
        }
        for i, entry in enumerate(filtered)
    ]

# ========== 会話API（/chat） ==========
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    character = data.get("character", "random")
    system_prompt = character_prompts.get(character, character_prompts["random"])
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print("Chat Error:", e)
        return jsonify({"reply": "Sorry, something went wrong."}), 500

# ========== 添削API（/correct） ==========
@app.route("/correct", methods=["POST"])
def correct():
    data = request.get_json()
    user_sentence = data.get("message")
    character = data.get("character", "random")

    correction_prompt = f"""
あなたは英語学習者向けの英文添削者です。
ユーザーから英語の文が与えられたら、以下の形式でフィードバックしてください：

1. original: 入力された英文（そのまま表示）
2. correction: 正しい文に修正したもの（英文で）
3. grammar: 原文のどこがどう間違っていて、なぜ間違いなのかを日本語で説明してください。
4. naturalness: より自然で伝わりやすい英語表現があれば例文で提示（1～2文）
5. alternative: 意味を保った自然な言い換え（なければ "-"）

出力形式（純粋なJSON文字列のみ）：
{{
  "original": "...",
  "correction": "...",
  "grammar": "...",
  "naturalness": "...",
  "alternative": "..."
}}

現在の会話相手（キャラクター設定）は「{character}」です。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": correction_prompt},
                {"role": "user", "content": user_sentence}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(reply_text)
        except json.JSONDecodeError:
            print("⚠️ JSONパース失敗:", reply_text)
            parsed = {
                "original": user_sentence,
                "correction": "",
                "grammar": "⚠️ JSON形式での出力に失敗しました。",
                "naturalness": "",
                "alternative": ""
            }
        return jsonify({"reply": parsed})
    except Exception as e:
        print("Correction Error:", e)
        return jsonify({
            "reply": {
                "original": user_sentence,
                "correction": "",
                "grammar": "申し訳ありません、文法チェック中にエラーが発生しました。",
                "naturalness": "",
                "alternative": ""
            }
        }), 500

# ========== Flask起動 ==========
if __name__ == "__main__":
    app.run(debug=True)
