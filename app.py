from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# SQLite のデータベース設定（読み込み専用）
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
print(f"データベースのパス: {db_path}")

# SQLiteの読み込み専用設定
db_uri = f"sqlite:///{db_path}?mode=ro"  # `mode=ro` を追加
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy で読み込み専用のエンジンを作成
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(f"sqlite:///{db_path}", connect_args={"uri": True, "mode": "ro"})  # 読み込み専用
Session = sessionmaker(bind=engine)
session = Session()

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
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM audio_files").fetchall()
        if result:
            for row in result:
                print(f"ID: {row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}")
        else:
            print("データベースにデータがありません。")

# Flask 起動前にデータを表示
print("===== データベースの内容を表示 =====")
# print_database_contents()

# API: `/audio_data/all` にアクセスするとデータを返す
@app.route("/audio_data/all", methods=["GET"])
def get_audio_data():
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM audio_files").fetchall()
        if result:
            audio_data = [{"id": row[0], "verb": row[1], "verb_jp": row[2], "sentence": row[3], "sentence_jp": row[4], "path": row[5]} for row in result]
            return app.response_class(
                response=json.dumps(audio_data, ensure_ascii=False, indent=4),
                status=200,
                mimetype="application/json"
            )
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
