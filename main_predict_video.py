import os
import time
from threading import Thread

import cv2

from sqlalchemy import create_engine

import predict_video2
from db.config import PostgresConfig
from db.database import DataBase, DBSession
from db.queries.progress import update_progress, delete_progress, delete_video_from_queue


def create_image_preview(path_to_video, path_to_save_im):
    vidcap = cv2.VideoCapture(path_to_video)
    success, image = vidcap.read()
    cv2.imwrite(path_to_save_im, image)


def detect_new_video(session: DBSession, new_video):
    file_name = new_video.video_name
    # try:
    predict_video2.predict_video_outside(
        os.path.join('raw_files', file_name),
        os.path.join(*['web', 'static', 'raw', file_name[:-4] + '2.mp4']),
        session,
        new_video.id
    )
    update_progress(session, new_video.id, 100)
    session.set_video_done(new_video.id)
    session.commit_session()
    create_image_preview(os.path.join(*['web', 'static', 'raw', file_name]),
                         os.path.join(*['web', 'static', 'raw', 'frames', file_name[:-4] + '.png']))
    # except:
    #     print('bad_format_video')
    #     delete_progress(session, new_video.id)
    #     delete_video_from_queue(session, new_video.id)
    session.close_session()


def main_predict_video():
    config = PostgresConfig()
    engine = create_engine(
        name_or_url=config.url,
        pool_pre_ping=True,  # if session dropped, it'll automatically launched
    )
    database = DataBase(connection=engine)
    database.check_connection()

    if not os.path.exists(os.path.join(*['web', 'static', 'raw'])):
        os.makedirs(os.path.join(*['web', 'static', 'raw']))
        os.makedirs(os.path.join(*['web', 'static', 'raw', 'frames']))
    if not os.path.exists('raw_files'):
        os.makedirs('raw_files')
    while True:
        session: DBSession = database.make_session()
        new_video = session.get_last_video_from_queue()
        if new_video:
            session.set_is_in_progress(new_video.id)
            session.commit_session()
            session.set_is_in_progress(new_video.id)
            Thread(target=detect_new_video,
                  args=(database.make_session(), new_video)).start()
        else:
            session.close_session()
            time.sleep(0.5)


if __name__ == '__main__':
    main_predict_video()
