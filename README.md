# ASCII Player

[<img src="bad_apple.gif" width="500"/>](picameleon.png)

This player plays video on a terminal using ascii characters

There are 2 versions, one is plain python the other ones uses cython optimizations.

A good example are high contrast videos like `bad apple`, you can download it from youtube with `youtube-dl` from [here](https://www.youtube.com/watch?v=FtutLA63Cp8) or just use the url directly in the command line and the player will stream it to your terminal.

## Youtube Explanation

I made a [youtube video](https://www.youtube.com/watch?v=ASJ3iY0-qpQ&ab_channel=Esser50K) explaining how the general process of converting videos to ascii

And [another video](https://youtu.be/i9Zj2qN0uJ8) on how it was ported for the raspberryPi.

## Install dependencies

`pip3 install -r requirements.txt`

## Usage

After having a file you can play it like this:

```
python3 player.py <path_to_video or youtube_video_url or video_input_device_index>
```

The player uses 120 characters as default width. This can be changed using the `--width` flag. The height is calculated to preserve the aspect ratio.

The default framerate is 30 fps. This can also be changed using the `--fps` flag. If it's set too high it will just go as fast as it can.

You can choose to display the original video with `opencv` with `--show true`

You can also choose to invert the shades of the ascii video with `--inv true`

You can also choose to use actual colors with `--color true`. You might need to `reset` the terminal afterwards since it overrides default colors.

### Webcam Usage

To use your webcam as video source simply specify the video input device index, most likely it is `0` unless you have multiple ones in which case  you  can just bruteforce your way through until you find it.

## Cython Version Usage

The regular python version is already pretty efficient even for larger screens, but cython can go even faster!

First make sure you have `cython` installed you can install it with `pip3 install cython`

Then compile the cython code: `cython -3 painter.pyx`. This will generate the `painter.c` file.

Now you can run the `cplayer.py` the same way as the other player.

You can try maxing out the framerate, in the end the average fps will be printed and you can see the difference there.

## Running on a raspberrypi

For best results run on a raspberrypi5 with the cython version as that gets the best framerate at higher resolutions.

### Install dependencies

Install the `Picamera2` and `opencv` dependencies via apt:

```
sudo apt install python3-opencv python3-picamera2
```

Create a virtual environment that still has access to the system packages an install the remaining dependencies:

```
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip3 install -r requirements_rpi.txt
```

### Embed Watermark

You can embed a txt file as watermark with the `--embed` flag. It will be printed on the right bottom of the screen.

As an examlpe I added a QR code that points to my [youtube channel](https://www.youtube.com/@esser50k)

```
python3 cplayer.py --width 350 --embed esser50k_yt.txt 0
```