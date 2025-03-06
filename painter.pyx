import cython
import numpy
import color
import curses
from libc.string cimport strchr, strlen
from functools import lru_cache

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
char_range = int(255 / len(characters))


def invert_chars():
    global characters
    characters = characters[::-1]


@lru_cache
def get_char(val):
    return characters[min(int(val / char_range), len(characters) - 1)]


@cython.boundscheck(False)
cpdef paint_screen(
    window,
    unsigned char[:, :] grayscale_frame,
    int width,
    int height,
):
    cdef int x, y

    for y in range(0, grayscale_frame.shape[0]):
        for x in range(0, grayscale_frame.shape[1]):
            try:
                window.addch(y, x, get_char(grayscale_frame[y, x]))
            except:
                pass


@cython.boundscheck(False)
cpdef paint_color_screen(window, 
                         unsigned char[:, :] grayscale_frame, 
                         unsigned char[:, :, :] frame, 
                         int width, 
                         int height,
                         curses_color):
    cdef int y, x, row_width, current_color, start_x
    row_width = frame.shape[1]
    
    for y in range(frame.shape[0]):
        # Precompute the color for each pixel in this row.
        row_colors = [curses_color.get_color(tuple(frame[y, x])) for x in range(row_width)]
        
        x = 0
        while x < row_width:
            current_color = row_colors[x]
            start_x = x
            segment_chars = []
            while x < row_width and row_colors[x] == current_color:
                segment_chars.append(get_char(grayscale_frame[y, x]))
                x += 1
            try:
                window.addstr(y, start_x, "".join(segment_chars), curses.color_pair(current_color))
            except curses.error:
                pass


@cython.boundscheck(False)
cpdef paint_embedding(window, const char * embed, int height, int fullwidth, int fullheight):
    cdef int x, y
    cdef int line_idx = 0
    cdef int line_length = 0
    cdef const char * start = embed
    cdef const char * end
    cdef const char * startptr

    while start[0] != b'\0':
        end = strchr(start, b'\n')

        if end == NULL:
            end = strchr(start, b'\0')

        line_length = end - start
        startptr = start
        while startptr < end:
            try:
                x = fullwidth - line_length + (startptr - start)
                y = fullheight - height + line_idx
                window.addch(y, x, startptr[0])
                startptr += 1
            except:
                return

        line_idx += 1
        if line_idx == height:
            return

        start = end + 1
