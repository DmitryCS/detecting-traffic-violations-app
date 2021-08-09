import json
import os

import cv2


def lines_to_json():
    num_lines = 6
    dts = list(dict())
    for i in range(1, num_lines+1):
        dt, dt2 = dict(), dict()
        minx, maxx = 10**5, -1
        im = cv2.imread(os.path.join(*['images', f'line{i}.png']))
        h, w = len(im), len(im[0])
        for x in range(w):
            for y in range(h):
                if sum(im[y][x]) == 255*3:
                    minx = min(x, minx)
                    maxx = max(x, maxx)
                    if x in dt.keys():
                        dt[x].append(y)
                    else:
                        dt[x] = list()
                        dt[x].append(y)
        for k, v in dt.items():
            dt2[k] = sum(v) / len(v) + 0.001
        dt2['minx'] = minx
        dt2['maxx'] = maxx
        dts.append(dt2)
    with open('lines0.json', 'w') as outfile:
        json.dump(dts, outfile)


# def green_lines_to_json():
#     num_lines = 1
#     dts = list(dict())
#     for i in range(1, num_lines+1):
#         dt, dt2 = dict(), dict()
#         miny, maxy = 10**5, -1
#         im = cv2.imread(os.path.join(*['images', f'line_green{i}.png']))
#         h, w = len(im), len(im[0])
#         for y in range(h):
#             for x in range(w):
#                 if sum(im[y][x]) == 255*3:
#                     miny = min(y, miny)
#                     maxy = max(y, maxy)
#                     if y in dt.keys():
#                         dt[y].append(x)
#                     else:
#                         dt[y] = list()
#                         dt[y].append(x)
#         for k, v in dt.items():
#             dt2[k] = sum(v) / len(v) + 0.001
#         dt2['miny'] = miny
#         dt2['maxy'] = maxy
#         dts.append(dt2)
#     with open('green_lines.json', 'w') as outfile:
#         json.dump(dts, outfile)

if __name__=='__main__':
    lines_to_json()
    # green_lines_to_json()
