from flask import Blueprint, request, jsonify
from openai import OpenAI
import os

bp = Blueprint("chat", __name__, url_prefix="/chat")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

character_prompts = {
    "tutor": "You are a kind and patient English tutor...",
    "random": "You are a friendly English speaker..."
}

@bp.route("", methods=["POST"])
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
