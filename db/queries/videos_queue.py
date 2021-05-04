from typing import List

from db.database import DBSession
from db.models import DBVideoQueue


def add_video_in_queue(session: DBSession, file_name) -> int:
    video_id = session.add_model_video(DBVideoQueue(video_name=file_name))
    return video_id


def get_list_videos(session: DBSession) -> List[DBVideoQueue]:
    videos = session.get_video_queue()
    return videos
