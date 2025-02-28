from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# SQLite のデータベース設定
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
print(f"データベースのパス: {db_path}")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# データベースのモデル
class AudioFile(db.Model):
    __tablename__ = "audio_files"
    id = db.Column(db.Integer, primary_key=True)
    verb = db.Column(db.TEXT, nullable=False)
    verb_jp = db.Column(db.TEXT, nullable=False)
    sentence = db.Column(db.TEXT, nullable=False)
    sentence_jp = db.Column(db.TEXT, nullable=False)
    path = db.Column(db.TEXT, nullable=False)

# **データベースの内容を取得 & 表示**
def print_database_contents():
    with app.app_context():
        files = AudioFile.query.all()  # 全データ取得
        print(files)
        if files:
            for file in files:
                print(f"ID: {file.id}, {file.verb}, {file.verb_jp}, {file.sentence}, {file.sentence_jp}, {file.path}")
        else:
            print("データベースにデータがありません。")

# Flask 起動前にデータを表示
print("===== データベースの内容を表示 =====")
# print_database_contents()

# API: `/audio_data/all` にアクセスするとデータを返す
@app.route("/audio_data/all", methods=["GET"])
def get_audio_data():
    audio_data = AudioFile.query.all()
    if audio_data:
        audio_data = [{"id": file.id, "verb": file.verb, "verb_jp":file.verb_jp, "sentence":file.sentence, "sentence_jp":file.sentence_jp, "path":file.path} for file in audio_data]
        return app.response_class(
        response=json.dumps(audio_data, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
