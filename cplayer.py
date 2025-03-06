import os
import cv2
import curses
import argparse
import time
import color
import youtube_utils

import pyximport
pyximport.install()

from painter import paint_screen, paint_color_screen, paint_embedding, invert_chars

parser = argparse.ArgumentParser(description='ASCII Player')
parser.add_argument("--width", type=int, default=120,
                    help="width of the terminal window")
parser.add_argument("--fps", type=int, default=30,
                    help="width of the terminal window")
parser.add_argument("--show", type=bool, default=False,
                    help="show the original video in an opencv window")
parser.add_argument("--inv", type=bool, default=False,
                    help="invert the shades")
parser.add_argument("--color", type=bool, default=False,
                    help="print colors if available in the terminal (slows things down a lot)")
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

fps = 0
frame_count = 0
frames_per_ms = args.fps / 1000
start = time.perf_counter_ns() // 1000000

try:
    if type(video) is str \
       and not os.path.isfile(video) \
       and not youtube_utils.is_youtube_url(video):
        print("failed to find video at:", args.video)

    if youtube_utils.is_youtube_url(video):
        video = youtube_utils.get_youtube_video_url(video)

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
    if args.color and curses.can_change_color():
        curses.start_color()
        curses.use_default_colors()
    window = curses.newwin(height, width, 0, 0)

    curses_color = color.CursesColor()

    while True:
        ok, orig_frame = video.read()
        if not ok:
            break

        frame = cv2.resize(orig_frame, (width, height))
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if args.show:
            cv2.imshow("frame", orig_frame)
            cv2.waitKey(1)

        if args.color and curses.can_change_color():
            paint_color_screen(window, grayscale_frame,
                               frame, width, height, curses_color)
        else:
            paint_screen(window, grayscale_frame, width, height)

        paint_embedding(window, embedding.encode(),
                        embed_height, width, height)

        elapsed = (time.perf_counter_ns() // 1000000) - start
        supposed_frame_count = frames_per_ms * elapsed
        if frame_count > supposed_frame_count:
            time.sleep((frame_count - supposed_frame_count)
                       * (1 / frames_per_ms) / 1000)
        window.refresh()
        frame_count += 1
        elapsed_time_seconds = (
            time.perf_counter_ns() // 1000000 - start) / 1000
        if elapsed_time_seconds > 1:
            fps = frame_count / elapsed_time_seconds
            frame_count = 0
            start = time.perf_counter_ns() // 1000000
finally:
    cv2.destroyAllWindows()
    curses.endwin()
    print("played at %d fps" % fps)
