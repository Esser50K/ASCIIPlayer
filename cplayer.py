import os
import cv2
import curses
import argparse
import time

import pyximport
pyximport.install()

from painter import paint_screen, paint_embedding, invert_chars


parser = argparse.ArgumentParser(description='ASCII Player')
parser.add_argument("--width", type=int, default=120,
                    help="width of the terminal window")
parser.add_argument("--fps", type=int, default=30,
                    help="width of the terminal window")
parser.add_argument("--show", type=bool, default=False,
                    help="show the original video in an opencv window")
parser.add_argument("--inv", type=bool, default=False,
                    help="invert the shades")
parser.add_argument("--embed", type=str, default="",
                    help="pass a txt file to embed as watermark")
parser.add_argument("video", type=str, help="path to video or webcam index")
args = parser.parse_args()
width = args.width

if args.inv:
    invert_chars()

video = args.video
try:
    video = int(video)
except ValueError:
    pass

embedding = ""
if args.embed != "":
    with open(args.embed, "r") as f:
        embedding = f.read()
embed_height = len(embedding.split("\n"))

frame_count = 0
frames_per_ms = args.fps / 1000
start = time.perf_counter_ns() // 1000000

try:
    if type(video) is str and not os.path.isfile(video):
        print("failed to find video at:", args.video)

    video = cv2.VideoCapture(video)
    ok, frame = video.read()
    if not ok:
        print("could not extract frame from video")

    ratio = width / frame.shape[1]
    # character height is 3/5 times character width
    height = int(frame.shape[0] * ratio * (3.0 / 5))
    print(frame.shape)
    print(width, height, ratio)

    curses.initscr()
    window = curses.newwin(height, width, 0, 0)

    while True:
        ok, orig_frame = video.read()
        if not ok:
            break

        frame = cv2.resize(orig_frame, (width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if args.show:
            cv2.imshow("frame", orig_frame)
            cv2.waitKey(1)

        paint_screen(window, frame, width, height)
        paint_embedding(window, embedding.encode(), embed_height, width, height)

        elapsed = (time.perf_counter_ns() // 1000000) - start
        supposed_frame_count = frames_per_ms * elapsed
        if frame_count > supposed_frame_count:
            time.sleep((frame_count - supposed_frame_count)
                       * (1 / frames_per_ms) / 1000)
        window.refresh()
        frame_count += 1
finally:
    cv2.destroyAllWindows()
    curses.endwin()
    fps = frame_count / (((time.perf_counter_ns() // 1000000) - start) / 1000)
    print("played on average at %d fps" % fps)
