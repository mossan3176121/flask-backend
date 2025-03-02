from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
from sqlalchemy import create_engine, Column, Integer, Text, MetaData, Table
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app)

# SQLite のデータベース設定（読み込み専用）
db_path = os.path.join(os.path.dirname(__file__), "audio_files.db")
db_uri = f"sqlite:///{db_path}?mode=ro&uri=true"  # SQLite の読み込み専用モード

print(f"データベースのパス: {db_path}")
print(f"データベース URI: {db_uri}")

# SQLAlchemyのエンジンを作成（読み込み専用）
try:
    engine = create_engine(db_uri, echo=True)
    print("✅ データベース接続成功")
except Exception as e:
    print(f"❌ データベース接続エラー: {e}")

# メタデータの取得（テーブル定義を取得）
metadata = MetaData()
try:
    audio_files = Table(
        "audio_files", metadata,
        Column("id", Integer, primary_key=True),
        Column("verb", Text, nullable=False),
        Column("verb_jp", Text, nullable=False),
        Column("sentence", Text, nullable=False),
        Column("sentence_jp", Text, nullable=False),
        Column("path", Text, nullable=False),
    )
    print("✅ テーブル定義の取得成功")
except Exception as e:
    print(f"❌ テーブル定義の取得エラー: {e}")

# API: `/audio_data/all` にアクセスするとデータを返す
@app.route("/audio_data/all", methods=["GET"])
def get_audio_data():
    try:
        with engine.connect() as conn:
            print("🔍 クエリ実行中...")
            result = conn.execute(audio_files.select()).fetchall()
            print(f"🔍 取得データ数: {len(result)}")
            if result:
                audio_data = [{"id": row[0], "verb": row[1], "verb_jp": row[2], "sentence": row[3], "sentence_jp": row[4], "path": row[5]} for row in result]
                return app.response_class(
                    response=json.dumps(audio_data, ensure_ascii=False, indent=4),
                    status=200,
                    mimetype="application/json"
                )
        print("⚠ データが見つかりませんでした")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
