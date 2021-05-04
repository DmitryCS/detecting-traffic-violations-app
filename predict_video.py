from configs import Config

import numpy as np
import cv2

# для регистрации данных
from detectron2.data.datasets import register_coco_instances

# для предиктора
from db.queries.progress import update_progress
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog

# для предсказания фото
from detectron2.utils.visualizer import ColorMode

# для предсказания видео
import tqdm
from detectron2.utils.video_visualizer import VideoVisualizer
import copy
import os
import time

from sort.sort import Sort

my_cfg = Config()
# register_coco_instances(my_cfg.dataset_name, {}, my_cfg.path_to_json, my_cfg.path_to_dataset)
register_coco_instances(my_cfg.dataset_name, {}, '', '')
MetadataCatalog.get(my_cfg.dataset_name).thing_classes = ['car', 'minibus', 'trolleybus', 'tram', 'truck', 'bus', 'middle_bus', 'ambulance', 'fire_truck', 'middle_truck', 'tractor', 'uncategorized', 'van', 'person']
dataset_metadata = MetadataCatalog.get(my_cfg.dataset_name)
print(dataset_metadata)


def apply_mask(image, mask, color, alpha=0.5):
    """
        Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(mask == 0, image[:, :, c] * (1 - alpha) + alpha * color[c] * 255, image[:, :, c])
    return image


def create_mask(path_to_mask, w, h):
  mask = cv2.imread(path_to_mask,cv2.IMREAD_GRAYSCALE) #"drive/My Drive/Colab Notebooks/My_files_detectron2/mask.png"
  print(w,h)
  mask = cv2.resize(mask, dsize=(w, h))
  mask = mask.astype(np.bool)
  return mask


# Функции, необходимые для обработки видеофайла
def _frame_from_video(video):
  while video.isOpened():
      success, frame = video.read()
      if success:
          yield frame
      else:
        break


def draw_label(image, value, pos, color=(255, 255, 255), size=1, shadow=False, shadow_color=None):
    # if color is None:
    #     color = [255, 255, 255]
    size = int(size)
    weight = size / 2
    offset = int(size / 2)

    if shadow:
        if shadow_color is None:
            shadow_color = [0, 0, 0]
        shadow_size = size + 4
        shadow_offset = offset + 2

        cv2.putText(image, str(value), (int(pos[0]) + shadow_offset, int(pos[1]) + shadow_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, weight, shadow_color, shadow_size)

    cv2.putText(image, str(value), (int(pos[0]) + offset, int(pos[1]) + offset), cv2.FONT_HERSHEY_SIMPLEX, weight,
                color, size)


def line_rgb_to_bool(image, h, w):
    line_bool = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if image[i][j][0] == 255:
               line_bool[i][j] = 1
    return line_bool


def around_line(line_bool, h, w):
    reg = [[0] * w for _ in range(h)]
    w_3 = 0
    for j in range(w):
        one = False
        for i in range(h):
            if line_bool[i][j] == 1:
                # white line
                one = True
                reg[i][j] = 1
            elif not one:
                # black upper line
                reg[i][j] = 2
            else:
                break
        if not one:
            w_3 = j
            break
    for i in range(h):
        for j in range(w_3, w):
            # after line right
            reg[i][j] = 3
    return reg

line = cv2.imread(my_cfg.path_to_mask_line)
h, w = len(line), len(line[0])
line_bool = line_rgb_to_bool(line, h, w)

reg_zones = around_line(line_bool, h, w)

track_ids_to_zones = {}
track_ids_to_zones_list = {}


def get_position_on_zones(center, reg_zones):
    #     hx,wy = min(int(center[0]), 1079), min(int(center[1]), 1919)
    hx,wy = int(center[1]), int(center[0])
    return reg_zones[hx][wy]


def run_on_video(video):
        video_visualizer = VideoVisualizer(dataset_metadata, ColorMode.IMAGE)

        def process_predictions(frame, predictions, track_ids):
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            predictions = predictions["instances"].to("cpu")
            boxes = outputs['instances'].pred_boxes.tensor.to("cpu").numpy()
            for i in range(len(track_ids)):
                box = boxes[i]
                track_id = track_ids[i]
                # draw_label(frame, track_id, box[:2], size=2, shadow=True)
                if track_id != 0 and -1 in track_ids_to_zones[track_id]:
                    draw_label(frame, "Solid line crossing", box[:2], size=2, shadow=True)
            vis_frame = video_visualizer.draw_instance_predictions(frame, predictions)
            # Converts Matplotlib RGB format to OpenCV BGR format
            vis_frame = cv2.cvtColor(vis_frame.get_image(), cv2.COLOR_RGB2BGR)
            return vis_frame

        frame_gen = _frame_from_video(video)
        for frame in frame_gen:
            frame_with_mask = apply_mask(copy.deepcopy(frame), mask, [0,0,0], 1)
            outputs = predictor(frame_with_mask)
            boxes = outputs['instances'].pred_boxes.tensor.to("cpu").numpy()
            scores = outputs['instances'].scores.to("cpu").numpy()
            # Обновляем трекер, получаем track_id (id объекта на предыдущих кадрах) для каждого найденного объекта
            for_tracker = np.concatenate([boxes, scores[:, None]], axis=1)
            dets, associaties = tracker.update(for_tracker, make_associaties=True)
            if type(associaties) is not list:
                track_ids = associaties.tolist()
            track_ids = associaties
            for i in range(len(track_ids)):
                inst = boxes[i]
                min_x, min_y = min(inst[0], inst[2]), min(inst[1], inst[3])
                temp_center_bbox = [min_x + abs((inst[0] - inst[2]) / 2),
                                    min_y + abs((inst[1] - inst[3]) / 2)]
                pos_on_zone = get_position_on_zones(temp_center_bbox, reg_zones)
                if track_ids[i] not in track_ids_to_zones.keys():
                    track_ids_to_zones[track_ids[i]] = {pos_on_zone}
                elif pos_on_zone not in track_ids_to_zones[track_ids[i]] and pos_on_zone != 3:
                    track_ids_to_zones[track_ids[i]].add(pos_on_zone)
                    if len(track_ids_to_zones[track_ids[i]]) == 3:
                        track_ids_to_zones[track_ids[i]].add(-1)
                if track_ids[i] not in track_ids_to_zones_list.keys():
                    track_ids_to_zones_list[track_ids[i]] = [pos_on_zone]
                else:
                    track_ids_to_zones_list[track_ids[i]].append(pos_on_zone)

            yield process_predictions(frame, outputs, track_ids)


def predict_video_outside(path_to_video, path_to_save_video, session, progress_id):
    start_time = time.time()
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    # "LVISv0.5-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"))  # получение используемой модели
    cfg.MODEL.WEIGHTS = my_cfg.path_to_weights  # model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml") #my_cfg.path_to_weights  # "model_final.pth" # путь к найденным лучшим весам модели
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.51  # установить порог распознавания объекта в 50% (объекты, распознанные с меньшей вероятностью не будут учитываться)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 13  # число классов для распознавания
    global predictor, tracker, mask, frame_gen
    predictor = DefaultPredictor(cfg)
    tracker = Sort(max_age=40)

    # Предсказание видео
    video = cv2.VideoCapture(path_to_video)  # my_cfg.video_file_name
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))

    mask = create_mask(my_cfg.path_to_mask, w, h)

    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    # if to_mp4:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # else:
    #     fourcc = cv2.VideoWriter_fourcc(*'VP80')
    output_file = cv2.VideoWriter(path_to_save_video, fourcc, fps, (w, h),
                                  True)  # my_cfg.video_file_name_to_save

    frame_gen = _frame_from_video(video)

    index_for = 0
    for vis_frame in tqdm.tqdm(run_on_video(video), total=num_frames):
        print("it's here:", int(index_for / num_frames * 100))
        if index_for % 10:
            update_progress(session, progress_id, int(index_for / num_frames * 100))
        output_file.write(vis_frame)
        index_for += 1
    update_progress(session, progress_id, 99)
    video.release()
    output_file.release()
    os.system(
        f"ffmpeg -i {path_to_save_video} -vcodec libx264 {path_to_save_video[:-5] + '.mp4'}")
    os.remove(path_to_video)
    os.remove(path_to_save_video)
    print(time.time() - start_time)


if __name__ == '__main__':
    # os.system(f"ffmpeg -i {my_cfg.video_file_name_to_save} -vcodec libx264 {my_cfg.video_file_name_to_save} -y")
    # exit()
    start_time = time.time()
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
        #"LVISv0.5-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"))  # получение используемой модели
    cfg.MODEL.WEIGHTS =  my_cfg.path_to_weights #model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml") #my_cfg.path_to_weights  # "model_final.pth" # путь к найденным лучшим весам модели
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.51  # установить порог распознавания объекта в 50% (объекты, распознанные с меньшей вероятностью не будут учитываться)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 13  # число классов для распознавания

    predictor = DefaultPredictor(cfg)
    tracker = Sort(max_age=40)

    #Предсказание видео
    video = cv2.VideoCapture(my_cfg.video_file_name) #my_cfg.video_file_name
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))

    mask = create_mask(my_cfg.path_to_mask, w, h)

    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    # if to_mp4:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # else:
    #     fourcc = cv2.VideoWriter_fourcc(*'VP80')
    output_file = cv2.VideoWriter(my_cfg.video_file_name_to_save, fourcc, fps, (w, h), True) # my_cfg.video_file_name_to_save

    frame_gen = _frame_from_video(video)

    for vis_frame in tqdm.tqdm(run_on_video(video), total=num_frames):
        output_file.write(vis_frame)
    # with open('your_file.txt', 'w') as f:
    #     for key in track_ids_to_zones_list.keys():
    #         f.write("%s " % str(key))
    #         for l in track_ids_to_zones_list[key]:
    #             f.write("%s " % str(l))
    #         f.write("\n")
    video.release()
    output_file.release()
    os.system(f"ffmpeg -i {my_cfg.video_file_name_to_save} -vcodec libx264 {my_cfg.video_file_name_to_save[:-4]+'2.mp4'}")
    print(time.time() - start_time)