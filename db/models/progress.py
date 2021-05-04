from sqlalchemy import Column, VARCHAR, Integer, BOOLEAN, ForeignKey

from db.models import BaseModel


class DBProgress(BaseModel):

    __tablename__ = 'progress'

    queue_id = Column(
        Integer,
        ForeignKey('videos_queue.id'),
        nullable=False,
    )
    progress_percentage = Column(
        Integer,
        nullable=False,
    )
    is_delete = Column(
        BOOLEAN(),
        nullable=False,
        default=False
    )
