# ASCII Player

[<img src="bad_apple.gif" width="500"/>](picameleon.png)

This player plays video on a terminal using ascii characters

There are 2 versions, one is plain python the other ones uses cython optimizations.

A good example are high contrast videos like `bad apple`, you can download it from youtube with `youtube-dl` from [here](https://www.youtube.com/watch?v=FtutLA63Cp8)

## Install dependencies

`pip3 install -r requirements.txt`

## Usage

After having a file you can play it like this:

```
python3 player.py <video>
```

The player uses 120 characters as default width. This can be changed using the `--width` flag. The height is calculated to preserve the aspect ratio.

The default framerate is 30 fps. This can also be changed using the `--fps` flag. If it's set too high it will just go as fast as it can.

You can choose to display the original video with `opencv` with `--show true`

You can also choose to invert the shades of the ascii video with `--inv true`

## Cython Version Usage

The regular python version is already pretty efficient even for larger screens, but cython can go even faster!

First make sure you have `cython` installed you can install it with `pip3 install cython`

Then compile the cython code: `cython -3 painter.pyx`. This will generate the `painter.c` file.

Now you can run the `cplayer.py` the same way as the other player.

You can try maxing out the framerate, in the end the average fps will be printed and you can see the difference there.