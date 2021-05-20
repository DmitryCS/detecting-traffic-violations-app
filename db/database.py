from typing import List

from sqlalchemy import false, and_, desc, asc, true
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import sessionmaker, Session, Query

from db.exceptions import DBIntegrityException, DBDataException
# from db.models import BaseModel, DBUser, DBMessage, DBFile, DBMsgFile, DBProgress, DBVideoQueue
from db.models import  BaseModel, DBProgress, DBVideoQueue


class DBSession:
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def query(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)

    # def users(self) -> Query:
    #     return self._session.query(DBUser)
    #
    # def messages(self, without_deleted: bool = True) -> Query:
    #     if without_deleted:
    #         return self._session.query(DBMessage).filter(DBMessage.is_delete == false())
    #     else:
    #         return self._session.query(DBMessage)
    #
    # def files(self, without_deleted: bool = True) -> Query:
    #     if without_deleted:
    #         return self._session.query(DBFile).filter(DBFile.is_delete == false())
    #     else:
    #         return self._session.query(DBFile)
    #
    # def msgs_files(self, without_deleted: bool = True) -> Query:
    #     if without_deleted:
    #         return self._session.query(DBMsgFile).filter(DBMsgFile.is_delete == false())
    #     else:
    #         return self._session.query(DBFile)

    def close_session(self):
        self._session.close()

    def add_model(self, model: BaseModel):
        try:
            self._session.add(model)
        except IntegrityError as e:
            raise DBIntegrityException(e)
        except DataError as e:
            raise DBDataException(e)

    def add_model_progress(self, model: BaseModel):
        try:
            self._session.add(model)
            self.commit_session()
            m = self._session.query(DBProgress).filter(DBProgress.id == model.queue_id).first()
            return m.id
        except IntegrityError as e:
            raise DBIntegrityException(e)
        except DataError as e:
            raise DBDataException(e)

    def check_existing_hash(self, hash_video) -> DBVideoQueue:
        return self._session.query(DBVideoQueue).filter(DBVideoQueue.hash_video == hash_video).first()

    def add_model_video(self, model: BaseModel):
        try:
            self._session.add(model)
            self.commit_session()
            m = self._session.query(DBVideoQueue).filter(DBVideoQueue.video_name == model.video_name).first()
            return m.id
        except IntegrityError as e:
            raise DBIntegrityException(e)
        except DataError as e:
            raise DBDataException(e)

    # def get_user_by_login(self, login: str) -> DBUser:
    #     return self.users().filter(DBUser.login == login).first()
    #
    # def get_user_by_id(self, uid: int) -> DBUser:
    #     return self.users().filter(DBUser.id == uid).first()
    #
    # def get_file_by_id(self, file_id: int, *, without_deleted: bool = True) -> DBFile:
    #     return self.files(without_deleted).filter(DBFile.id == file_id).first()
    #
    # def get_msgfile_by_msgfile_ids(self, msg_id: int, file_id: int, *, without_deleted: bool = True) -> List[DBMsgFile]:
    #     return self.msgs_files(without_deleted).filter(
    #         and_(DBMsgFile.msg_id == msg_id, DBMsgFile.file_id == file_id)
    #     ).first()
    #
    # def get_msgfiles_by_msg_id(self, msg_id: int, *, without_deleted: bool = True) -> List[DBMsgFile]:
    #     return self.msgs_files(without_deleted).filter(DBMsgFile.msg_id == msg_id).all()
    #
    # def get_msgfiles_by_file_id(self, file_id: int, *, without_deleted: bool = True) -> List[DBMsgFile]:
    #     return self.msgs_files(without_deleted).filter(DBMsgFile.file_id == file_id).all()
    #
    # def get_message_by_id(self, message_id: int, *, without_deleted: bool = True) -> DBMessage:
    #     return self.messages(without_deleted).filter(DBMessage.id == message_id).first()
    #
    # def get_message(self, message_id: int, *, without_deleted: bool = True) -> DBMessage:
    #     return self.messages(without_deleted).filter(DBMessage.id == message_id).first()
    #
    # def get_all_messages(self, uid: int, *, without_deleted: bool = True) -> List[DBMessage]:
    #     return self.messages(without_deleted).filter(DBMessage.recipient_id == uid).all()

    def update_progress_by_id(self, pid: int, percantage: int) -> None:
        self._session.query(DBProgress).filter(DBProgress.id == pid).first().progress_percentage = percantage

    def delete_progress_by_id(self, pid: int) -> None:
        self._session.query(DBProgress).filter(DBProgress.id == pid).first().is_delete = true()

    def get_progress_by_id(self, pid: int) -> DBProgress:
        return self._session.query(DBProgress).filter(DBProgress.id == pid).first()

    def get_last_video_from_queue(self) -> DBVideoQueue:
        return self._session.query(DBVideoQueue).filter(
            and_(DBVideoQueue.is_done == false(),
                 DBVideoQueue.is_delete == false())).order_by(asc(DBVideoQueue.id)).first()

    def delete_video_from_queue_by_pid(self, pid: int) -> None:
        self._session.query(DBVideoQueue).filter(DBVideoQueue.id == pid).first().is_delete = true()

    def set_video_done(self, video_id):
        self._session.query(DBVideoQueue).filter(DBVideoQueue.id == video_id).first().is_done = true()

    def get_video_queue(self):
        return self._session.query(DBVideoQueue).filter(and_(DBVideoQueue.is_done == true(), DBVideoQueue.is_delete == false()))

    def commit_session(self, need_close: bool = False):
        try:
            self._session.commit()
        except IntegrityError as e:
            raise DBIntegrityException(e)
        except DataError as e:
            raise DBDataException(e)

        if need_close:
            self.close_session()


class DataBase:
    connection: Engine
    session_factory: sessionmaker
    _test_query = 'SELECT 1'

    def __init__(self, connection: Engine):
        self.connection = connection
        self.session_factory = sessionmaker(bind=self.connection)

    def check_connection(self):
        self.connection.execute(self._test_query).fetchone()

    def make_session(self) -> DBSession:
        session = self.session_factory()
        return DBSession(session)
