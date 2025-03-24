from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import json

bp = Blueprint("correct", __name__, url_prefix="/correct")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@bp.route("", methods=["POST"])
def correct():
    data = request.get_json()
    user_sentence = data.get("message")
    character = data.get("character", "random")

    correction_prompt = f"""
あなたは英語学習者向けの英文添削者です。
（中略）
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
            parsed = {
                "original": user_sentence,
                "correction": "",
                "grammar": "⚠️ JSON形式での出力に失敗しました。",
                "naturalness": "",
                "alternative": ""
            }
        return jsonify({"reply": parsed})
    except Exception as e:
        return jsonify({
            "reply": {
                "original": user_sentence,
                "correction": "",
                "grammar": "申し訳ありません、文法チェック中にエラーが発生しました。",
                "naturalness": "",
                "alternative": ""
            }
        }), 500
