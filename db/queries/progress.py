from db.database import DBSession
from db.models import DBProgress


def create_progress(session: DBSession, vid: int) -> int:
    progress_id = session.add_model_progress(DBProgress(queue_id=vid, progress_percentage=0))
    return progress_id


def update_progress(session: DBSession, progress_id: int, percentage: int) -> None:
    session.update_progress_by_id(progress_id, percentage)
    session.commit_session()


def get_progress_percantage(session: DBSession, progress_id: int) -> int:
    db_progress = session.get_progress_by_id(progress_id)
    if db_progress is not None:
        return db_progress.progress_percentage
    else:
        return -1
