from sqlalchemy import Column, VARCHAR, BOOLEAN

from db.models import BaseModel


class DBVideoQueue(BaseModel):

    __tablename__ = 'videos_queue'

    video_name = Column(VARCHAR(4096))
    hash_video = Column(VARCHAR(100))
    is_done = Column(
        BOOLEAN(),
        nullable=False,
        default=False
    )
    is_delete = Column(
        BOOLEAN(),
        nullable=False,
        default=False
    )
