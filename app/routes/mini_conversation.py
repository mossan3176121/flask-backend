from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.audio import MiniConversationFile, Base
import os

bp = Blueprint("mini_conversation", __name__, url_prefix="/api")

@bp.route('/submit', methods=['POST'])
def submit_input():
    data = request.get_json()
    scene_name = data.get("input", "")
    
    print("受信した入力:", scene_name)

    try:
        db_path = get_db_path(scene_name)
        db_uri = f"sqlite:///file:{os.path.abspath(db_path)}?mode=ro&uri=true"
        engine = create_engine(db_uri, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
    
        audio_data = session.query(MiniConversationFile).all()
        print("📢 audio_data の件数:", len(audio_data))
        return jsonify([
            {
                "scene": scene_name,
                "id": file.id,
                "start_time": file.start_time,
                "end_time": file.end_time,
                "speaker": file.speaker,
                "sentence": file.sentence,
                "path": file.path
            } for file in audio_data
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_db_path(scene_name):
    # 使用可能なシーン一覧を限定しておく（ホワイトリスト方式）
    # allowed_scenes = {"travel_tourism_1",
    #                   "daily_life_1",
    #                   "travel_tourism_2,",
    #                   "travel_tourism_3"}

    allowed_scenes = set(item.value for item in AllowedScenes)

    if scene_name not in allowed_scenes:
        raise ValueError("許可されていない scene_name です")

    base_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(os.path.join(base_dir, f"../data/mini_conversation/{scene_name}.db"))

    # セーフガード：パスが `../data` 内かどうか確認（トラバーサル防止）
    data_dir = os.path.abspath(os.path.join(base_dir, "../data"))
    if not db_path.startswith(data_dir):
        raise ValueError("不正なパスです")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"{db_path} が見つかりません")

    return db_path

from enum import Enum

class AllowedScenes(str, Enum):
    TRAVEL_1 = "travel_tourism_1"
    DAILY_1 = "daily_life_1"
    TRAVEL_2 = "travel_tourism_2"
    TRAVEL_3 = "travel_tourism_3"