import os
import time
import cv2

from sqlalchemy import create_engine

import predict_video
from db.config import PostgresConfig
from db.database import DataBase
from db.queries.progress import update_progress


def create_image_preview(path_to_video, path_to_save_im):
    vidcap = cv2.VideoCapture(path_to_video)
    success, image = vidcap.read()
    cv2.imwrite(path_to_save_im, image)


def main_predict_video():
    config = PostgresConfig()
    engine = create_engine(
        name_or_url=config.url,
        pool_pre_ping=True,  # if session dropped, it'll automatically launched
    )
    database = DataBase(connection=engine)
    database.check_connection()

    while True:
        session = database.make_session()
        new_video = session.get_last_video_from_queue()
        if new_video:
            file_name = new_video.video_name
            predict_video.predict_video_outside(
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
        else:
            session.close_session()
            time.sleep(0.5)


if __name__ == '__main__':
    main_predict_video()
