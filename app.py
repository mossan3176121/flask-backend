from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app)

# SQLite のデータベース設定 (読み取り専用)
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
db_uri = f"sqlite:///file:{db_path}?mode=ro&uri=true"

# SQLAlchemyのエンジンを作成 (読み取り専用)
engine = create_engine(db_uri, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# ベースクラスの定義
Base = declarative_base()

# データベースのモデル
class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True)
    verb = Column(Text, nullable=False)
    verb_jp = Column(Text, nullable=False)
    sentence = Column(Text, nullable=False)
    sentence_jp = Column(Text, nullable=False)
    path = Column(Text, nullable=False)

# **データベースの内容を取得 & 表示**
def print_database_contents():
    with app.app_context():
        files = session.query(AudioFile).all()  # 読み取り専用で取得
        if files:
            for file in files:
                print(f"ID: {file.id}, {file.verb}, {file.verb_jp}, {file.sentence}, {file.sentence_jp}, {file.path}")
        else:
            print("データベースにデータがありません。")

# Flask 起動前にデータを表示
# print("===== データベースの内容を表示 =====")
# print_database_contents()

# API: /audio_data/all にアクセスするとデータを返す
@app.route("/audio_data/all", methods=["GET"])
def get_audio_data():
    audio_data = session.query(AudioFile).all()
    if audio_data:
        audio_data = [{"id": file.id, "verb": file.verb, "verb_jp": file.verb_jp, "sentence": file.sentence, "sentence_jp": file.sentence_jp, "path": file.path} for file in audio_data]
        return app.response_class(
            response=json.dumps(audio_data, ensure_ascii=False, indent=4),
            status=200,
            mimetype="application/json"
        )
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
