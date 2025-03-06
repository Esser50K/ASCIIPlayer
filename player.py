import os
import cv2
import curses
import argparse
import time
import numpy as np
import color
import youtube_utils
from functools import lru_cache

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

video = args.video
try:
    video = int(video)
except ValueError:
    pass

width = args.width
characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
if args.inv:
    characters = characters[::-1]
char_range = int(255 / len(characters))


@lru_cache
def get_char(val):
    return characters[min(int(val / char_range), len(characters) - 1)]


def paint_screen(window, frame):
    for y in range(0, frame.shape[0]):
        for x in range(0, frame.shape[1]):
            try:
                window.addch(y, x, get_char(frame[y, x]))
            except (curses.error):
                pass


def paint_color_screen(window, grayscale_frame, frame, curses_color: color.CursesColor):
    for y in range(0, frame.shape[0]):
        for x in range(0, frame.shape[1]):
            try:
                color = curses_color.get_color(tuple(frame[y, x]))
                window.addch(y, x,
                             get_char(grayscale_frame[y, x]),
                             curses.color_pair(color))
            except (curses.error):
                pass


def paint_embedding(window: curses.window, embedding: str, embedding_height: int, grayscale_frame):
    for line_idx, line in enumerate(embedding.split("\n")):
        line_len = len(line)
        width = grayscale_frame.shape[1]
        height = grayscale_frame.shape[0]
        try:
            window.addstr(
                height - embedding_height + line_idx,
                width - line_len,
                line
            )
        except:
            pass


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
    # charachter height is 2 times character width
    height = int(frame.shape[0] * ratio * 3 / 5)
    print(frame.shape)
    print(width, height, ratio)

    curses.initscr()
    if args.color and curses.can_change_color():
        curses.start_color()
        curses.use_default_colors()
        curses_color = color.CursesColor()
    window = curses.newwin(height, width, 0, 0)

    embedding = ""
    if args.embed != "":
        with open(args.embed, "r") as f:
            embedding = f.read()
    embedding_height = len(embedding.split("\n"))

    fps = 0
    frame_count = 0
    frames_per_ms = args.fps / 1000
    start = time.perf_counter_ns() // 1000000
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
                               frame.astype(np.int32), curses_color)
        else:
            paint_screen(window, grayscale_frame)

        paint_embedding(window, embedding, embedding_height, grayscale_frame)

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
