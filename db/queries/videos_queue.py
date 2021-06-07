from typing import List

from db.database import DBSession
from db.models import DBVideoQueue


def add_video_in_queue(session: DBSession, file_name, hash_video) -> int:
    video_id = session.add_model_video(DBVideoQueue(video_name=file_name, hash_video=hash_video))
    return video_id


def get_list_videos(session: DBSession) -> List[DBVideoQueue]:
    videos = session.get_video_queue()
    return videos


def check_existing_hash(session: DBSession, hash_video) -> bool:
    if session.check_existing_hash(hash_video):
        return True
    return False


def get_num_violathions_by_videoid(session: DBSession, video_id: int) -> int:
    return session.get_num_violathions_by_videoid(video_id).violations_num
