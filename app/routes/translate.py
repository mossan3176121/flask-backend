from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import json
import random

bp = Blueprint("translate", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("sentence_pairs.json", "r", encoding="utf-8") as f:
    sentence_pairs = json.load(f)

@bp.route("/get_question", methods=["GET"])
def get_question():
    question = random.choice(sentence_pairs)
    return jsonify({
        "japanese": question["japanese"],
        "correct": question["english"]
    })

@bp.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    japanese = data.get("japanese")
    correct = data.get("correct")
    user_answer = data.get("english")

    prompt = f"""
（翻訳評価のGPT用プロンプト）
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    reply = response.choices[0].message.content
    try:
        parsed = json.loads(reply)
        return jsonify(parsed)
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "GPTの出力がJSONとして読み取れませんでした。",
            "raw_reply": reply,
            "details": str(e)
        }), 500
