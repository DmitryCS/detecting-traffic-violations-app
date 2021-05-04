from sqlalchemy import Column, VARCHAR, LargeBinary

from db.models import BaseModel


class DBPost(BaseModel):

    __tablename__ = 'posts'

    login = Column(VARCHAR(50), unique=True, nullable=False)
