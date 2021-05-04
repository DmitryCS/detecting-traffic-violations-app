import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    host = os.getenv('host', 'localhost')
    port = int(os.getenv('port', 8000))
    workers = int(os.getenv('workers', 1))
    debug = bool(os.getenv('debug', False))

    dataset_name = os.getenv('dataset_name', 'my_dataset')
    path_to_dataset = os.getenv('path_to_dataset', '')
    path_to_json = os.getenv('path_to_json', '')
    work_dir = os.getenv('work_dir', '')
    path_to_weights = os.getenv('path_to_weights', '')
    path_to_mask = os.getenv('path_to_mask', '')
    path_to_mask_line = os.getenv('path_to_mask_line', '')
    video_file_name = os.getenv('video_file_name', 'video.mp4')
    video_file_name_to_save = os.getenv('video_file_name_to_save', 'video_final.mp4')
    photo_file_name = os.getenv('photo_file_name', 'images/out.png')
    photo_file_name_to_save = os.getenv('photo_file_name_to_save', 'images/out_final.png')
