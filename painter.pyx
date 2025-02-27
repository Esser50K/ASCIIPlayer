import cython
from libc.string cimport strchr, strlen
from functools import lru_cache

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
char_range = int(255 / len(characters))

def invert_chars():
    global characters
    characters = characters[::-1]

@lru_cache
def get_char(val):
    return characters[min(int(val/char_range), len(characters)-1)]

@cython.boundscheck(False)
cpdef paint_screen(window, unsigned char [:, :] frame, int width, int height):
    cdef int x, y

    for y in range(0, frame.shape[0]):
        for x in range(0, frame.shape[1]):
            try:                
                window.addch(y, x, get_char(frame[y, x]))
            except:
                pass

@cython.boundscheck(False)
cpdef paint_embedding(window, const char* embed, int height, int fullwidth, int fullheight):
    cdef int x, y
    cdef int line_idx = 0
    cdef int line_length = 0
    cdef const char* start = embed
    cdef const char* end
    cdef const char* startptr

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
