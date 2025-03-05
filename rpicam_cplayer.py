#!/usr/bin/python3

import os
import cv2
import curses
import time
import argparse
import pyximport
pyximport.install()

from painter import paint_screen, paint_embedding, invert_chars
from picamera2 import Picamera2

parser = argparse.ArgumentParser(description='ASCII Player for Raspberry Pi')
parser.add_argument("--width", type=int, default=120,
                    help="Width of the terminal window")
parser.add_argument("--fps", type=int, default=30, help="Frames per second")
parser.add_argument("--show", action="store_true",
                    help="Show the original video in an OpenCV window")
parser.add_argument("--inv", action="store_true", help="Invert the shades")
parser.add_argument("--embed", type=str, default="",
                    help="pass a txt file to embed as watermark")

args = parser.parse_args()

width = args.width
if args.inv:
    invert_chars()

embedding = ""
if args.embed != "":
    with open(args.embed, "r") as f:
        embedding = f.read()
embed_height = len(embedding.split("\n"))

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"format": "RGB888", "size": (1920, 1080)}))
picam2.start()
picam2.set_controls({
    # Enable Auto Exposure (ensures proper brightness)
    "AeEnable": True,
    # Enable Auto White Balance (ensures proper colors)
    "AwbEnable": True,
    # High-quality noise reduction (matches ISP processing)
    "NoiseReductionMode": 3,
    "Sharpness": 1.0,         # Match rpicam-still sharpness
    "Contrast": 1.0,          # Prevent washed-out image
    "Saturation": 1.2,        # Slight color boost (adjust if needed)
    "ScalerCrop": (348, 434, 1920, 1080),  # Ensure full frame is used
    "ColourGains": (1.5, 1.5)  # Try matching CFE color correction
})
time.sleep(2)

# Capture first frame to determine height
frame = picam2.capture_array()
ratio = width / frame.shape[1]
height = int(frame.shape[0] * ratio * (3.0 / 5))  # Character height correction

curses.initscr()
window = curses.newwin(height, width, 0, 0)

frame_count = 0
frames_per_ms = args.fps / 1000
start = time.perf_counter_ns() // 1000000

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, (width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        if args.show:
            cv2.imshow("frame", frame)
            cv2.waitKey(1)

        paint_screen(window, frame, width, height)
        paint_embedding(window, embedding.encode(),
                        embed_height, width, height)

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
    print("Played on average at %d fps" % fps)
    picam2.stop()
