from flask import Blueprint, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from app.utils.youtube import extract_video_id
import re
import traceback

bp = Blueprint("subtitles", __name__, url_prefix="/get_subtitles")

@bp.route("", methods=["POST"])
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
